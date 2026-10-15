import socket
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock
import requests
from connection_tools import ipv4_get, diagnose_url

class TransportTests(unittest.TestCase):
    def test_ipv4_preserves_tls_and_manual_redirect(self):
        def run(command, **kwargs):
            self.assertIn('--ipv4',command)
            self.assertNotIn('--insecure',command)
            self.assertNotIn('--location',command)
            Path(command[command.index('--dump-header')+1]).write_text('HTTP/1.1 200 Connection established\r\n\r\nHTTP/2 302\r\nLocation: /next\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n')
            Path(command[command.index('--output')+1]).write_bytes('本文'.encode())
            return SimpleNamespace(returncode=0,stdout='302')
        with patch('connection_tools.subprocess.run',side_effect=run):
            r=ipv4_get('https://example.com',{},(30,30))
        self.assertTrue(r.is_redirect)
        self.assertEqual(r.headers['location'],'/next')
        self.assertEqual(r.text,'本文')
    def test_curl_timeout_is_retryable(self):
        with patch('connection_tools.subprocess.run',return_value=SimpleNamespace(returncode=28)):
            with self.assertRaises(requests.Timeout): ipv4_get('https://example.com',{},(30,30))
    def test_missing_curl_has_actionable_message(self):
        with patch('connection_tools.subprocess.run',side_effect=FileNotFoundError):
            with self.assertRaisesRegex(ValueError,'packages.txt'): ipv4_get('https://example.com',{},30)
    def test_diagnosis_rejects_local_destination(self):
        with patch('connection_tools.socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,0,'',('127.0.0.1',443))]), patch('connection_tools.socket.socket') as conn:
            r=diagnose_url('https://example.com',lambda u:u)
        conn.assert_not_called()
        self.assertIn('公開IP以外',r['rows'][-1]['結果'])
    def test_diagnosis_shows_tcp_timeout(self):
        sock=Mock()
        sock.__enter__=Mock(return_value=sock)
        sock.__exit__=Mock(return_value=False)
        sock.connect.side_effect=TimeoutError()
        with patch('connection_tools.socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,0,'',('8.8.8.8',443))]), patch('connection_tools.socket.socket',return_value=sock):
            r=diagnose_url('https://example.com',lambda u:u)
        self.assertEqual(r['rows'][-1]['結果'],'失敗：タイムアウト')

if __name__=='__main__': unittest.main()
