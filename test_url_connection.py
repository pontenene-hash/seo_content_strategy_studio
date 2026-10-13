import ast
from pathlib import Path
from unittest.mock import Mock
import unittest
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

class ConnectionTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path('app.py').read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'fetch_page')
        self.http = Mock(wraps=requests)
        for name in ('Timeout','ConnectionError','HTTPError','exceptions'):
            setattr(self.http,name,getattr(requests,name))
        self.sleep = Mock()
        self.env = dict(requests=self.http, BeautifulSoup=BeautifulSoup, urljoin=urljoin,
                        validate_public_url=lambda u:u, PAGE_REQUEST_TIMEOUT=(30,30), MAX_PAGE_CHARS=18000,
                        time=Mock(sleep=self.sleep))
        exec(compile(ast.Module(body=[node],type_ignores=[]),'app.py','exec'),self.env)
    def response(self, status=200):
        r=Mock(status_code=status, is_redirect=False, is_permanent_redirect=False,
               headers={'content-type':'text/html'},text='<article>'+ '本文です。'*100+'</article>')
        if status>=400: r.raise_for_status.side_effect=requests.HTTPError()
        return r
    def test_timeout_then_success(self):
        self.http.get.side_effect=[requests.ConnectTimeout(),self.response()]
        self.assertIn('本文です',self.env['fetch_page']('https://example.com')['text'])
        self.assertEqual(self.http.get.call_count,2)
        self.sleep.assert_called_once_with(2)
    def test_timeout_is_bounded_and_friendly(self):
        self.http.get.side_effect=requests.ConnectTimeout('raw internal data')
        with self.assertRaisesRegex(ValueError,'本文を入力'):
            self.env['fetch_page']('https://example.com')
        self.assertEqual(self.http.get.call_count,2)
    def test_403_not_retried(self):
        self.http.get.return_value=self.response(403)
        with self.assertRaisesRegex(ValueError,'アクセスが拒否'):
            self.env['fetch_page']('https://example.com')
        self.assertEqual(self.http.get.call_count,1)
    def test_temporary_503_retries(self):
        self.http.get.side_effect=[self.response(503),self.response()]
        self.env['fetch_page']('https://example.com')
        self.assertEqual(self.http.get.call_count,2)

if __name__ == '__main__': unittest.main()
