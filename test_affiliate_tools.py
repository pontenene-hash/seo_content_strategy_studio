import ast
import json
import unittest
from html import escape
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import affiliate_tools as a
from reset_tools import reset_article_state


BODY = "# 商品の選び方\n\n悩みに合う選び方を紹介します。\n\n## 特徴\n資料にある特徴です。\n\n## 注意点\n購入条件を確認しましょう。\n\n## まとめ\n自分に合うか確認しましょう。"
RESULT = dict(intent="検索意図", outline="## 特徴\n## 注意点\n## まとめ", article=BODY, description="説明", checks="価格と条件を確認してください。")
LINK = "https://example.com/track?a=1&b=%2Fitem(x)&code=ABC"


def converter():
    tree = ast.parse(Path(__file__).with_name("app.py").read_text())
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "markdown_to_wordpress_html")
    scope = {"escape": escape, "re": __import__("re")}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "app.py", "exec"), scope)
    return scope[fn.name]


class AffiliateTests(unittest.TestCase):
    def test_exact_tracking_url_and_escaped_html(self):
        from bs4 import BeautifulSoup
        md, html = a.assemble_article(BODY + '\n<script>alert(1)</script>', LINK, '<購入>', 'https://example.com/source', converter())
        soup = BeautifulSoup(html, "html.parser")
        ads = soup.select('a[rel~=sponsored]')
        self.assertEqual(len(ads), 3)
        self.assertTrue(all(x['href'] == LINK for x in ads))
        self.assertTrue(all(x.get_text() == '<購入>' for x in ads))
        self.assertIsNone(soup.find('script'))
        self.assertEqual(md.count(a.DISCLOSURE), 1)
        self.assertIn('参考：元記事', md)

    def test_invalid_links(self):
        for value in ['javascript:alert(1)', '<a href="x">', 'https://user:pass@example.com', 'http://127.0.0.1', 'http://localhost/x', 'https://example.com/ x']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                a.validate_link(value)

    def test_competition_requires_matching_real_research(self):
        r = dict(keyword='クッション 選び方', context='実際の競合分析', demo_mode=False)
        self.assertEqual(a.competitor_context(r, r['keyword']), r['context'])
        for result, keyword in [(None, 'x'), (dict(r, demo_mode=True), r['keyword']), (r, '別の商品')]:
            with self.assertRaises(ValueError):
                a.competitor_context(result, keyword)

    def test_prompt_and_model_output(self):
        prompt = a.build_prompt('商品の仕様。' * 50, '商品A', '選び方', '働く方', 4000, '実体験', '競合分析資料')
        self.assertIn('競合分析資料', prompt)
        self.assertIn('原文の丸写し', prompt)
        result = a.generate_affiliate(None, 'test', prompt, lambda *args, **kw: json.dumps(RESULT))
        self.assertEqual(result['article'], BODY)
        for raw in ['{"article":', '{}', json.dumps(dict(RESULT, article=BODY + '\nhttps://unknown.example'))]:
            with self.assertRaises(ValueError):
                a.generate_affiliate(None, 'test', prompt, lambda *args, **kw: raw)

    def test_reset_preserves_settings_clears_new_mode(self):
        state = dict(affiliate_result=RESULT, affiliate_link=LINK, affiliate_edited_body=BODY,
                     seo_result={}, social_plan={}, api_key='keep', social_brand_name='ぽんて')
        reset_article_state(state)
        self.assertEqual(state, dict(api_key='keep', social_brand_name='ぽんて', _article_input_epoch=1))


class AffiliateUI(unittest.TestCase):
    def test_generate_edit_social_and_reset_without_live_api(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=20)
        at.secrets['GEMINI_API_KEY'] = 'mock-only'
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.tabs), 6)
        at.text_area(key='affiliate_source_body').input('元記事の商品説明です。' * 30)
        at.text_input(key='affiliate_product').input('商品A')
        at.text_input(key='affiliate_link').input(LINK)
        at.text_input(key='affiliate_keyword').input('クッション 選び方')
        with patch('google.genai.Client') as client:
            client.return_value.models.generate_content.return_value = SimpleNamespace(text=json.dumps(RESULT))
            at.button(key='affiliate_generate').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['affiliate_result']['link'], LINK)
        self.assertIn('sponsored', at.session_state['affiliate_result']['html_article'])
        self.assertIn('アフィリエイト記事の完成本文', at.selectbox(key='social_source').options)
        at.text_area(key='affiliate_edited_body').input(BODY + '\n編集した本文です。').run()
        at.selectbox(key='social_source').select('アフィリエイト記事の完成本文').run()
        self.assertTrue(any('編集した本文です。' in x.value for x in at.text_area if x.label == 'SNSへ展開する完成記事'))
        at.text_area(key='affiliate_edited_body').input(BODY + '\n再編集した本文です。').run()
        self.assertTrue(any('再編集した本文です。' in x.value for x in at.text_area if x.label == 'SNSへ展開する完成記事'))
        # 失敗した生成は直前の成果物を消さない。
        before = at.session_state['affiliate_result']['html_article']
        with patch('google.genai.Client') as client:
            client.return_value.models.generate_content.return_value = SimpleNamespace(text='{broken')
            at.button(key='affiliate_generate').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['affiliate_result']['html_article'], before)
        at.button(key='reset_article_top').click().run()
        self.assertFalse(at.exception)
        self.assertNotIn('affiliate_result', at.session_state)
        self.assertEqual(at.text_area(key='affiliate_source_body').value, '')


if __name__ == '__main__':
    unittest.main()
