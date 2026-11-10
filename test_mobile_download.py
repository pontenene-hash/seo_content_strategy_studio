import ast
import base64
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock

from download_tools import dated_filename
from mobile_download_tools import build_download_component, build_save_page


def scripts(html):
    return re.findall(r'<script>(.*?)</script>', html, re.S)


class MobileDownloadTests(unittest.TestCase):
    def test_untrusted_text_is_data_not_executable_html(self):
        payload = '\ufeff# 日本語\n</script><script>alert(1)</script>'.encode()
        filename = '</script>__LABEL__".md'
        html = build_download_component('<保存> __PAGE__', payload, filename, 'text/markdown')
        self.assertEqual(len(scripts(html)), 1)
        self.assertIn('&lt;保存&gt; __PAGE__', html)
        self.assertNotIn('<script>alert(1)', html)
        self.assertIn(base64.b64encode(payload).decode(), html)

    def test_both_save_modes_preserve_payload_and_ignore_reruns(self):
        tree = ast.parse(Path(__file__).with_name('app.py').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'safe_download_button')
        st = Mock(session_state={})
        render = Mock()
        scope = dict(st=st, render_mobile_download=render, dated_filename=dated_filename,
                     _download_sequence=iter(range(10)))
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'app.py', 'exec'), scope)
        scope[fn.name]('保存', '日本語', 'article.md', 'text/markdown', '20261110_234500')
        render.assert_called_once_with('保存', '日本語'.encode('utf-8-sig'), 'article_20261110_234500.md', 'text/markdown')
        st.download_button.assert_not_called()
        st.session_state['download_mode'] = '従来のダウンロード'
        scope[fn.name]('ZIP', b'bytes', 'bundle.zip', 'application/zip', '20261110_234500')
        kwargs = st.download_button.call_args.kwargs
        self.assertEqual(kwargs['data'], b'bytes')
        self.assertEqual(kwargs['file_name'], 'bundle_20261110_234500.zip')
        self.assertEqual(kwargs['on_click'], 'ignore')

    def test_ui_mode_switch_keeps_results_and_preference_survives_reset(self):
        from streamlit.testing.v1 import AppTest
        from test_affiliate_tools import RESULT, LINK
        at = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=20).run()
        at.session_state['affiliate_result'] = dict(RESULT, link=LINK, label='詳細', source_url='', product='商品A',
                                                   keyword='選び方', used_competition=False, prompt='生成指示')
        at.session_state['affiliate_edited_body'] = RESULT['article']
        at.session_state['affiliate_edited_link'] = LINK
        at.session_state['affiliate_edited_label'] = '詳細'
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.radio(key='download_mode').value, '別タブで保存（iPhone向け）')
        article = at.session_state['affiliate_result']['article']
        at.radio(key='download_mode').set_value('従来のダウンロード').run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['affiliate_result']['article'], article)
        at.button(key='reset_article_top').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.radio(key='download_mode').value, '従来のダウンロード')

    @unittest.skipUnless(shutil.which('node'), 'Node is needed for JavaScript logic tests')
    def test_new_tab_blocked_popup_return_copy_and_file_bytes(self):
        payload = '\ufeff# 本文\n<script>危険な文字列も実行しない</script>'.encode()
        page = build_save_page(payload, '日本語.md', 'text/markdown')
        fixtures = dict(component=scripts(build_download_component('保存', payload, '日本語.md', 'text/markdown'))[0],
                        page=scripts(page)[0], expectedPage=page, payload=base64.b64encode(payload).decode(),
                        binary=scripts(build_save_page(b'PK\x00\xff', 'a.zip', 'application/zip'))[0])
        js = r"""
const vm = require('node:vm'), assert = require('node:assert/strict');
let input=''; process.stdin.on('data', x=>input+=x);
process.stdin.on('end', async()=>{
  try {
    const f=JSON.parse(input);
    function doc() {
      const nodes={}; return {nodes, getElementById(id) {
        return nodes[id] ||= {hidden:true, textContent:'', handlers:{},
          addEventListener(type, fn){this.handlers[type]=fn},
          focus(){this.focused=true}, select(){this.selected=true}, setSelectionRange(a,b){this.range=[a,b]}};
      }};
    }
    let written='', opened=[], mainNavigated=false, closed=0;
    const popup={document:{open(){},write(html){written=html},close(){}},close(){closed++}};
    const main={open(...args){opened.push(args);return popup}};
    Object.defineProperty(main,'location',{set(){mainNavigated=true;throw Error('main navigation')}});
    const d=doc(), context=vm.createContext({window:main, document:d});
    vm.runInContext(f.component,context);
    d.nodes.open.handlers.click();
    assert.equal(opened.length,1); assert.equal(opened[0][1],'_blank');
    assert.equal(written,f.expectedPage); assert.equal(mainNavigated,false); assert.equal(popup.opener,null);
    main.open=()=>null;
    d.nodes.open.handlers.click();
    assert.match(d.nodes.status.textContent,/ポップアップ/); assert.equal(mainNavigated,false);
    main.open=()=>({document:{open(){throw Error('blocked')}},close(){closed++}});
    d.nodes.open.handlers.click(); assert.equal(closed,1); assert.match(d.nodes.status.textContent,/従来方式/);
    const p=doc(); let fileBlob, pageClosed=0, onhide, revoked=false;
    const pageContext=vm.createContext({document:p, window:{close(){pageClosed++},addEventListener(type,fn){onhide=fn}},
      navigator:{clipboard:{writeText:async()=>{throw Error('blocked')}}},
      URL:{createObjectURL(blob){fileBlob=blob;return 'blob:test'},revokeObjectURL(){revoked=true}},
      Blob, Uint8Array, TextDecoder, atob});
    vm.runInContext(f.page,pageContext);
    assert.equal(Buffer.from(await fileBlob.arrayBuffer()).toString('base64'),f.payload);
    assert.equal(fileBlob.type,'text/markdown'); assert.equal(p.nodes.save.download,'日本語.md');
    assert.equal(p.nodes.save.href,'blob:test'); assert.equal(p.nodes['text-section'].hidden,false);
    await p.nodes.copy.handlers.click(); assert.equal(p.nodes.text.selected,true);
    pageContext.navigator.clipboard.writeText=async text=>{assert.equal(text,p.nodes.text.value)};
    await p.nodes.copy.handlers.click(); assert.match(p.nodes['copy-feedback'].textContent,/コピーしました/);
    p.nodes.return.handlers.click(); assert.equal(pageClosed,1);
    onhide({persisted:true}); assert.equal(revoked,false);
    onhide({persisted:false}); assert.equal(revoked,true);
    const binaryDoc=doc();
    vm.runInNewContext(f.binary,{document:binaryDoc,window:{addEventListener(){}},navigator:{},
      URL:{createObjectURL(){return 'blob:zip'}}, Blob, Uint8Array,TextDecoder,atob});
    assert.equal(binaryDoc.nodes['text-section'],undefined);
    console.log('Separate-tab JavaScript checks passed');
  } catch(e) {console.error(e);process.exitCode=1}
});
"""
        result = subprocess.run(['node', '-e', js], input=json.dumps(fixtures), text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
