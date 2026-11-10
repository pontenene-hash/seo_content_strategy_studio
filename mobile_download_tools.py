"""保存を別タブへ分離し、元のStreamlitセッションを残す。"""
import base64
import json
import re
from html import escape


def _script_json(value):
    # HTMLパーサーがスクリプトを途中で閉じないよう、入力を文字参照ではなくJSONで保護する。
    return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def build_save_page(payload, filename, mime):
    encoded = base64.b64encode(payload).decode("ascii")
    data = _script_json({"base64": encoded, "filename": filename, "mime": mime})
    return """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ファイルの保存 | SEOコンテンツ戦略スタジオ</title>
<style>
*{box-sizing:border-box}body{font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#203547;background:#f3f6fa;margin:0;padding:24px 16px}
main{max-width:640px;margin:24px auto;background:white;border-radius:16px;padding:26px;box-shadow:0 4px 24px #20354710}
h1{font-size:24px;margin-top:0}#filename{overflow-wrap:anywhere;font-weight:600;background:#f3f6fa;padding:12px;border-radius:8px}
a,button{display:block;width:100%;text-align:center;border:0;border-radius:9px;padding:14px 18px;margin:14px 0;text-decoration:none;font:inherit;cursor:pointer}
a{background:#14776c;color:white}button{background:#e7edf4;color:#203547}small{color:#56687b}textarea{width:100%;min-height:220px;font:14px/1.6 monospace}#feedback{color:#14776c;min-height:1.5em}
</style></head><body><main>
<h1>ファイルを保存</h1>
<p>元のアプリは、元のタブに残っています。</p>
<p id="filename"></p>
<a id="save" target="_blank" rel="noopener">ファイルを保存する</a>
<p><small>ファイルの画面が開いた場合は「共有」→「ファイルに保存」を選んでください。その後、このタブへ戻るか、元のアプリのタブへ切り替えます。</small></p>
<button id="return" type="button">この保存タブを閉じてアプリへ戻る</button>
<p id="feedback" role="status"></p>
<section id="text-section" hidden><details><summary>本文を表示・コピーする</summary>
<p><small>下の本文は閲覧・コピー用です。編集は元のアプリで行ってください。</small></p>
<textarea id="text" aria-label="保存する本文" readonly></textarea>
<button id="copy" type="button">本文をコピー</button><p id="copy-feedback" role="status"></p>
</details></section>
</main><script>
const file = __DATA__;
const bytes = Uint8Array.from(atob(file.base64), c => c.charCodeAt(0));
const objectUrl = URL.createObjectURL(new Blob([bytes], {type:file.mime}));
document.getElementById('filename').textContent = file.filename;
const save = document.getElementById('save');
save.href = objectUrl;
save.download = file.filename;
document.getElementById('return').addEventListener('click', () => {
  document.getElementById('feedback').textContent = '閉じない場合は、ブラウザーのタブ一覧から元のアプリを選んでください。';
  window.close();
});
if (file.mime.startsWith('text/') || file.mime === 'application/json') {
  document.getElementById('text-section').hidden = false;
  const text = document.getElementById('text');
  text.value = new TextDecoder('utf-8').decode(bytes);
  document.getElementById('copy').addEventListener('click', async () => {
    const feedback = document.getElementById('copy-feedback');
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('unsupported');
      await navigator.clipboard.writeText(text.value);
      feedback.textContent = '本文をコピーしました。';
    } catch (_) {
      text.focus(); text.select(); text.setSelectionRange(0, text.value.length);
      feedback.textContent = '本文を選択しました。長押しなどで「コピー」を選んでください。';
    }
  });
}
window.addEventListener('pagehide', event => {if (!event.persisted) URL.revokeObjectURL(objectUrl);});
</script></body></html>""".replace("__DATA__", data)


def build_download_component(label, payload, filename, mime):
    page = _script_json(build_save_page(payload, filename, mime))
    template = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#526375}
button{box-sizing:border-box;width:100%;padding:11px 14px;border:1px solid #bdcbd7;border-radius:8px;background:#fff;color:#203547;font:inherit;cursor:pointer;min-height:44px;white-space:normal;overflow-wrap:anywhere}
button:hover{border-color:#14776c;color:#14776c}button:focus-visible{outline:3px solid #8ed7cd;outline-offset:1px}
p{font-size:12px;margin:6px 0}#status{color:#b53b2d}
</style></head><body>
<button id="open" type="button">__LABEL__</button>
<p>別タブで保存画面を開きます。元のアプリと生成結果は残ります。</p>
<p id="status" role="status" aria-live="polite"></p>
<script>
const savePage = __PAGE__;
document.getElementById('open').addEventListener('click', () => {
  // ユーザーのタップ内で同期的に開く。現在タブのlocationは変更しない。
  const tab = window.open('', '_blank');
  if (!tab) {
    document.getElementById('status').textContent = '別タブを開けませんでした。ポップアップを許可するか、左側の「保存方法」を切り替えてください。';
    return;
  }
  try {
    tab.opener = null;
    tab.document.open(); tab.document.write(savePage); tab.document.close();
    document.getElementById('status').textContent = '';
  } catch (_) {
    tab.close();
    document.getElementById('status').textContent = '保存画面を開けませんでした。左側の「保存方法」を従来方式へ切り替えてください。';
  }
});
</script></body></html>"""
    values = {"__PAGE__": page, "__LABEL__": escape(label)}
    return re.sub(r"__PAGE__|__LABEL__", lambda match: values[match.group()], template)


def render_mobile_download(label, payload, filename, mime):
    import streamlit as st
    component = build_download_component(label, payload, filename, mime)
    if hasattr(st, "iframe"):
        st.iframe(component, height="content", alt="別タブでファイルを保存")
    else:
        from streamlit.components.v1 import html
        html(component, height=160, scrolling=True)
