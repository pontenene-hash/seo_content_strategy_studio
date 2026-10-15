"""公開URLの接続診断と、明示選択するIPv4通信。TLS検証は維持する。"""
import ipaddress
import socket
import ssl
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse
import requests


def ipv4_get(url, headers, timeout, allow_redirects=False):
    """curlのIPv4モード。転送先には自動接続せず、呼出元が検証する。"""
    if allow_redirects:
        raise ValueError('自動リダイレクトは使用できません。')
    with tempfile.TemporaryDirectory() as folder:
        body = Path(folder) / 'body'
        head = Path(folder) / 'headers'
        command = ['curl', '--ipv4', '--silent', '--show-error', '--proto', '=http,https',
                   '--connect-timeout', '15', '--max-time', '30', '--max-filesize', '5000000',
                   '--dump-header', str(head), '--output', str(body), '--write-out', '%{http_code}',
                   '--user-agent', headers.get('User-Agent', ''), '--url', url]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=35)
        except FileNotFoundError as exc:
            raise ValueError('IPv4接続にはcurlが必要です。更新版packages.txtをGitHubへアップロードしてください。') from exc
        except subprocess.TimeoutExpired as exc:
            raise requests.Timeout() from exc
        if completed.returncode:
            if completed.returncode == 28:
                raise requests.Timeout()
            if completed.returncode in {51, 60}:
                raise requests.exceptions.SSLError()
            if completed.returncode == 63:
                raise ValueError('ページの容量が大きすぎます。本文を貼り付けてください。')
            raise requests.ConnectionError()
        response = requests.Response()
        response.status_code = int(completed.stdout.strip())
        response.url = url
        response._content = body.read_bytes()
        # 最後のHTTPヘッダーだけを利用（プロキシのCONNECT応答と分離）。
        for line in head.read_text(errors='replace').splitlines():
            if line.startswith('HTTP/'):
                response.headers.clear()
            elif ':' in line:
                key, value = line.split(':', 1)
                response.headers[key.strip()] = value.strip()
        response.encoding = requests.utils.get_encoding_from_headers(response.headers)
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
        return response


def diagnose_url(url, validate):
    """同一実行環境でDNS→TCP→TLSを測る。HTTP制限の有無は断定しない。"""
    started = time.monotonic()
    rows = []
    try:
        url = validate(url)
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        unique = []
        for family in (socket.AF_INET, socket.AF_INET6):
            candidates = [a for a in addresses if a[0] == family]
            if candidates:
                unique.append(candidates[0])
            else:
                rows.append({'方式': 'IPv4' if family == socket.AF_INET else 'IPv6', '段階': 'DNS', '結果': 'この方式の接続先なし（異常とは限りません）'})
        for family, socktype, proto, _, address in unique:
            kind = 'IPv4' if family == socket.AF_INET else 'IPv6'
            if not ipaddress.ip_address(address[0]).is_global:
                raise ValueError('公開IP以外には接続できません。')
            rows.append({'方式': kind, '段階': 'DNS', '結果': f'解決成功：{address[0]}'})
            stage = 'TCP接続'
            began = time.monotonic()
            try:
                with socket.socket(family, socktype, proto) as sock:
                    sock.settimeout(5)
                    sock.connect(address)
                    rows.append({'方式': kind, '段階': stage, '結果': f'成功（{time.monotonic()-began:.1f}秒）'})
                    if parsed.scheme == 'https':
                        stage = 'TLS証明書確認'
                        with ssl.create_default_context().wrap_socket(sock, server_hostname=host):
                            rows.append({'方式': kind, '段階': stage, '結果': '成功'})
            except (OSError, ssl.SSLError) as exc:
                label = 'タイムアウト' if isinstance(exc, TimeoutError) else type(exc).__name__
                rows.append({'方式': kind, '段階': stage, '結果': f'失敗：{label}'})
    except (ValueError, OSError) as exc:
        rows.append({'方式': '共通', '段階': 'URL・DNS確認', '結果': str(exc)})
    return {'url': url, 'rows': rows, 'seconds': round(time.monotonic()-started, 1)}
