import ast
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from urllib.parse import urljoin
from unittest.mock import Mock
from rewrite_tools import rewrite_article


class RewriteTests(unittest.TestCase):
    def test_source_and_instructions_reach_model(self):
        source = '正式店舗名・料金3,000円・条件を保持。' * 20
        expected = dict(article='# 改稿\n本文', changes='構成変更', checks='料金要確認', description='概要')
        llm = Mock(return_value=json.dumps(expected))
        result = rewrite_article(None, 'model', source, '整体', '地域の方', '読みやすさ', '名称維持', llm)
        self.assertEqual(result, expected)
        self.assertIn(source, llm.call_args.args[2])
        self.assertEqual(llm.call_args.kwargs['response_mime_type'], 'application/json')

    def test_invalid_input_does_not_call_model(self):
        llm = Mock()
        for source in ('短い', '長' * 30001):
            with self.assertRaises(ValueError):
                rewrite_article(None, '', source, '', '', '', '', llm)
        llm.assert_not_called()

    def test_truncated_and_missing_outputs_rejected(self):
        for output in ('{"article":', '{}', '[]'):
            with self.assertRaises(ValueError):
                rewrite_article(None, '', '文' * 100, '', '', '', '', Mock(return_value=output))

    def test_url_extraction_keeps_long_body_headings_and_citations(self):
        from bs4 import BeautifulSoup
        tree = ast.parse(Path('app.py').read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'fetch_page')
        html = '<title>題名</title><main><nav>不要ナビ</nav><article><header><h1>元の題名</h1></header><h2>重要な条件</h2><p>' + '本文' * 11000 + '</p><a href="/source">出典</a></article></main>'
        response = SimpleNamespace(is_redirect=False, is_permanent_redirect=False,
            headers={'content-type': 'text/html'}, text=html, status_code=200, raise_for_status=lambda: None)
        env = dict(BeautifulSoup=BeautifulSoup, requests=SimpleNamespace(get=Mock(return_value=response)),
            validate_public_url=lambda x: x, urljoin=urljoin, PAGE_REQUEST_TIMEOUT=20, MAX_PAGE_CHARS=18000)
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'app.py', 'exec'), env)
        result = env['fetch_page']('https://example.com/article', full_article=True)
        self.assertIn('# 元の題名', result['article'])
        self.assertIn('## 重要な条件', result['article'])
        self.assertIn('https://example.com/source', result['article'])
        self.assertGreater(len(result['article']), 22000)
        self.assertNotIn('不要ナビ', result['article'])
        self.assertLessEqual(len(env['fetch_page']('https://example.com/article')['text']), 18000)


if __name__ == '__main__':
    unittest.main()
