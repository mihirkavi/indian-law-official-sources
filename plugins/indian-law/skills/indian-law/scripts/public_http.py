"""Bounded public HTTPS retrieval, with source-specific origin and redirect checks."""
import http.client
import base64
import json
from pathlib import Path
import subprocess
import sys
import ipaddress
import socket
import ssl
import time
from urllib.parse import parse_qsl, urljoin, urlsplit

from casework import secret_key

MAX_BYTES = 15 * 1024 * 1024


class FetchError(ValueError):
    def __init__(self, status, reason):
        super().__init__(reason)
        self.status, self.reason = status, reason


def validate_url(url, hosts):
    try:
        if not isinstance(url, str) or len(url) > 4096 or any(ord(c) < 32 for c in url):
            raise ValueError()
        parsed = urlsplit(url)
        host = (parsed.hostname or '').lower()
        if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None, 443):
            raise ValueError()
        if host not in hosts or parsed.fragment or not parsed.path.startswith('/'):
            raise ValueError()
        if any(secret_key(key) for key, _ in parse_qsl(parsed.query, keep_blank_values=True)):
            raise ValueError()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError()
        return parsed
    except (ValueError, TypeError):
        raise FetchError('blocked_origin', 'URL is not an approved credential-free public HTTPS origin') from None


def public_addresses(host, resolver=socket.getaddrinfo):
    try:
        rows = resolver(host, 443, type=socket.SOCK_STREAM)
        addresses = list(dict.fromkeys(row[4][0] for row in rows))
        if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
            raise FetchError('blocked_origin', 'DNS must resolve only to public addresses')
        return addresses
    except FetchError:
        raise
    except (OSError, ValueError):
        raise FetchError('technical_failure', 'Public hostname resolution failed') from None


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, address, timeout):
        super().__init__(host, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        # No second DNS lookup: connect to the address already checked, with TLS hostname validation.
        raw = socket.create_connection((self.address, 443), timeout=self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def _request_once(url, max_bytes, timeout):
    parsed = urlsplit(url)
    addresses = public_addresses(parsed.hostname)
    connection = PinnedHTTPSConnection(parsed.hostname, addresses[0], timeout)
    started = time.monotonic()
    try:
        path = parsed.path + ('?' + parsed.query if parsed.query else '')
        connection.request('GET', path, headers={
            'User-Agent':'IndianLawResearch/0.2 (public legal document retrieval)',
            'Accept':'application/pdf,text/html,text/plain', 'Accept-Encoding':'identity'})
        response = connection.getresponse()
        headers = {key.lower():value for key, value in response.getheaders()}
        if response.status in (301,302,303,307,308) or response.status != 200:
            return response.status, headers, b''
        if headers.get('content-encoding','identity').lower() not in ('identity',''):
            raise FetchError('unexpected_content','Compressed HTTP response is unsupported')
        try:
            content_length = int(headers.get('content-length','0'))
        except ValueError:
            raise FetchError('unexpected_content','Invalid response length') from None
        if content_length > max_bytes:
            raise FetchError('size_limit','Document exceeds byte limit')
        chunks, size = [], 0
        while True:
            if time.monotonic() - started > timeout:
                raise FetchError('technical_failure','Document retrieval exceeded time limit')
            chunk = response.read(min(65536,max_bytes-size+1))
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                raise FetchError('size_limit','Document exceeds byte limit')
            chunks.append(chunk)
        return response.status, headers, b''.join(chunks)
    except FetchError:
        raise
    except (OSError, http.client.HTTPException, ValueError):
        raise FetchError('technical_failure','Public HTTPS retrieval failed; login necessity is unestablished') from None
    finally:
        connection.close()



def request_once(url, max_bytes, timeout):
    # Bound the entire request, including DNS, TLS, headers and slow-trickling bodies.
    try:
        result = subprocess.run([sys.executable,str(Path(__file__).resolve()),'--request'],
                                input=json.dumps({'url':url,'max_bytes':max_bytes,'timeout':timeout}).encode(),
                                capture_output=True,timeout=timeout)
        if result.returncode or len(result.stdout)>max_bytes*2+65536:
            raise FetchError('technical_failure','Public HTTPS request worker failed')
        payload=json.loads(result.stdout)
        if 'error' in payload:
            error=payload['error']
            raise FetchError(error['status'],error['reason'])
        return payload['status'],payload['headers'],base64.b64decode(payload['body'],validate=True)
    except subprocess.TimeoutExpired:
        raise FetchError('technical_failure','Overall public HTTPS time limit reached; no record verified') from None
    except FetchError:
        raise
    except (OSError,ValueError,KeyError,TypeError):
        raise FetchError('technical_failure','Public HTTPS request worker failed') from None


def fetch_public(url, hosts, max_bytes=MAX_BYTES, timeout=20, transport=None):
    transport = transport or request_once
    original, current, redirects, seen = url, url, [], set()
    deadline = time.monotonic()+timeout
    for _ in range(4):
        validate_url(current, hosts)
        if current in seen:
            raise FetchError('technical_failure','Redirect loop; no record verified')
        seen.add(current)
        remaining = deadline-time.monotonic()
        if remaining <= 0:
            raise FetchError('technical_failure','Retrieval time limit reached')
        status, headers, body = transport(current, max_bytes, remaining)
        if len(body) > max_bytes:
            raise FetchError('size_limit','Document exceeds byte limit')
        if status in (301,302,303,307,308):
            destination = urljoin(current, headers.get('location',''))
            validate_url(destination, hosts)
            redirects.append({'from':current,'to':destination,'http_status':status})
            current = destination
            continue
        if status != 200:
            raise FetchError('technical_failure',f'HTTP {status}; requested record not read; login necessity unestablished')
        return {'requested_url':original,'final_url':current,'redirects':redirects,
                'http_status':status,'content_type':headers.get('content-type','').split(';')[0].strip().lower(),
                'body':body}
    raise FetchError('technical_failure','Redirect hop limit reached')


if __name__=='__main__':
    if sys.argv[1:]!=['--request']:
        raise SystemExit(2)
    try:
        data=json.load(sys.stdin)
        status,headers,body=_request_once(data['url'],data['max_bytes'],data['timeout'])
        print(json.dumps({'status':status,'headers':headers,'body':base64.b64encode(body).decode()}))
    except FetchError as exc:
        print(json.dumps({'error':{'status':exc.status,'reason':exc.reason}}))
    except Exception:
        print(json.dumps({'error':{'status':'technical_failure','reason':'Public request failed'}}))
