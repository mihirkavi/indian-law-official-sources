import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/indian-law/skills/indian-law/scripts'
sys.path.insert(0, str(SCRIPTS))
from public_http import FetchError, fetch_public, validate_url, public_addresses
from documents import EvidenceStore, EvidenceError


def pdf_fixture(texts):
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'']
    kids = []
    for text in texts:
        page = len(objects) + 1
        content = page + 1
        kids.append(f'{page} 0 R')
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 600 800] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents {content} 0 R >>'.encode())
        lines = ['BT /F1 12 Tf 50 750 Td']
        for line in text.split('\n'):
            escaped = line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
            lines += [f'({escaped}) Tj', '0 -16 Td']
        stream = ('\n'.join(lines)+'\nET').encode()
        objects.append(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream')
    objects[1] = ('<< /Type /Pages /Count '+str(len(kids))+' /Kids ['+' '.join(kids)+'] >>').encode()
    data = b'%PDF-1.4\n'; offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data)); data += f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref = len(data)
    data += f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
    for offset in offsets[1:]: data += f'{offset:010d} 00000 n \n'.encode()
    return data + f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode()


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.registry = {'sources':[{'id':'court','name':'Court','publisher':'Court',
            'url':'https://court.gov.in/','official_provenance_url':'https://court.gov.in/',
            'enabled':True,'official':True,'verification_status':'page_inspected',
            'retrieval_hosts':['court.gov.in']} ]}
        self.pdf = pdf_fixture(['Caption\n1. Introductory text.', '2. Mutation does not confer title.'])
        self.calls = []
        self.responses = {'https://court.gov.in/order.pdf':(200,{'content-type':'application/pdf'},self.pdf)}
        def transport(url, max_bytes, timeout):
            self.calls.append(url)
            return self.responses[url]
        self.transport = transport
        self.store = EvidenceStore(Path(self.tmp.name)/'evidence', self.registry, transport=transport)

    def get(self): return self.store.fetch('court','https://court.gov.in/order.pdf')

    def test_download_has_real_hash_origin_and_page_indices(self):
        result = self.get()
        self.assertEqual(result['status'],'retrieved')
        self.assertEqual(result['sha256'],hashlib.sha256(self.pdf).hexdigest())
        self.assertEqual(result['page_count'],2)
        read = self.store.read(result['document_id'],pdf_page=2)
        self.assertIn('Mutation does not confer title.',read['pages'][0]['text'])
        self.assertEqual(read['pages'][0]['pdf_page'],2)
        self.assertIsNone(read['pages'][0]['printed_page'])

    def test_quote_at_correct_pdf_page_matches(self):
        r=self.get();checked=self.store.check_quote(r['document_id'],'Mutation does not confer title.',2)
        self.assertEqual(checked['status'],'matched')
        self.assertFalse(checked['legal_holding_verified'])

    def test_wrong_page_is_mismatch_not_silently_corrected(self):
        r=self.get();checked=self.store.check_quote(r['document_id'],'Mutation does not confer title.',1)
        self.assertEqual(checked['status'],'page_mismatch')
        self.assertEqual(checked['matched_pdf_pages'],[2])

    def test_false_quote_rejected(self):
        r=self.get();self.assertEqual(self.store.check_quote(r['document_id'],'Mutation proves ownership.',2)['status'],'not_found')

    def test_no_fuzzy_quote_repair(self):
        r=self.get();self.assertEqual(self.store.check_quote(r['document_id'],'Mutation does confer title.',2)['status'],'not_found')

    def test_unicode_and_whitespace_normalization(self):
        r=self.get();self.assertEqual(self.store.check_quote(r['document_id'],'Mutation\n  does not confer title.',2)['status'],'matched')

    def test_non_pdf_200_cannot_be_reported_as_pdf(self):
        self.responses['https://court.gov.in/order.pdf']=(200,{'content-type':'text/html'},b'<html><title>Access denied</title>Blocked</html>')
        self.assertEqual(self.get()['status'],'unexpected_content')

    def test_scanned_or_blank_pdf_not_invented(self):
        self.responses['https://court.gov.in/order.pdf']=(200,{'content-type':'application/pdf'},pdf_fixture(['']))
        self.assertEqual(self.get()['status'],'needs_ocr')

    def test_error403_is_not_login_and_has_no_document(self):
        self.responses['https://court.gov.in/order.pdf']=(403,{},b'forbidden')
        r=self.get();self.assertEqual(r['status'],'technical_failure');self.assertNotIn('document_id',r)

    def test_redirect_to_private_or_unofficial_host_blocked_before_request(self):
        self.responses['https://court.gov.in/order.pdf']=(302,{'location':'https://127.0.0.1/private'},b'')
        self.assertEqual(self.get()['status'],'blocked_origin')
        self.assertEqual(self.calls,['https://court.gov.in/order.pdf'])

    def test_same_host_redirect_retains_chain(self):
        self.responses['https://court.gov.in/order.pdf']=(302,{'location':'/final.pdf'},b'')
        self.responses['https://court.gov.in/final.pdf']=(200,{'content-type':'application/pdf'},self.pdf)
        r=self.get();self.assertEqual(r['final_url'],'https://court.gov.in/final.pdf');self.assertEqual(len(r['redirects']),1)

    def test_redirect_loop_is_bounded(self):
        self.responses['https://court.gov.in/order.pdf']=(302,{'location':'/order.pdf'},b'')
        self.assertEqual(self.get()['status'],'technical_failure');self.assertEqual(len(self.calls),1)

    def test_oversize_response_rejected(self):
        self.responses['https://court.gov.in/order.pdf']=(200,{'content-type':'application/pdf'},self.pdf+b'0'*10000)
        self.store.max_bytes=1000
        self.assertEqual(self.get()['status'],'size_limit')

    def test_disabled_or_unverified_source_not_requested(self):
        self.registry['sources'][0]['verification_status']='candidate_unverified'
        self.assertEqual(self.get()['status'],'blocked_origin');self.assertFalse(self.calls)

    def test_unknown_source_not_requested(self):
        self.assertEqual(self.store.fetch('private','https://court.gov.in/order.pdf')['status'],'blocked_origin');self.assertFalse(self.calls)

    def test_url_credentials_and_secret_query_rejected(self):
        for url in ['https://u:p@court.gov.in/order.pdf','https://court.gov.in/order.pdf?token=secret','https://court.gov.in/order.pdf?clientSecret=secret']:
            with self.subTest(url=url):self.assertEqual(self.store.fetch('court',url)['status'],'blocked_origin')
        self.assertFalse(self.calls)

    def test_suffix_trick_and_http_rejected(self):
        for url in ['https://court.gov.in.evil.test/x','http://court.gov.in/x','https://court.gov.in:444/x']:
            with self.subTest(url=url),self.assertRaises(FetchError):validate_url(url,{'court.gov.in'})

    def test_private_dns_answer_rejected(self):
        with self.assertRaises(FetchError):public_addresses('court.gov.in',resolver=lambda *a,**k:[(2,1,6,'',('127.0.0.1',443))])

    def test_all_dns_answers_checked(self):
        with self.assertRaises(FetchError):public_addresses('court.gov.in',resolver=lambda *a,**k:[(2,1,6,'',('8.8.8.8',443)),(2,1,6,'',('10.0.0.1',443))])

    def test_corrupted_text_is_rejected(self):
        r=self.get();p=Path(self.tmp.name)/'evidence'/r['document_id']/'pages.json';p.write_text('[]')
        with self.assertRaises(EvidenceError):self.store.read(r['document_id'])

    def test_corrupted_raw_is_rejected(self):
        r=self.get();p=Path(self.tmp.name)/'evidence'/r['document_id']/'document.bin';p.write_bytes(b'changed')
        with self.assertRaises(EvidenceError):self.store.read(r['document_id'])

    def test_document_id_cannot_escape_directory(self):
        with self.assertRaises(EvidenceError):self.store.read('../secrets')

    def test_query_returns_page_context(self):
        r=self.get();result=self.store.read(r['document_id'],query='mutation')
        self.assertEqual([p['pdf_page'] for p in result['pages']],[2])

    def test_html_does_not_execute_or_include_script_text(self):
        self.responses['https://court.gov.in/info']=(200,{'content-type':'text/html'},b'<html><title>Public notice</title><script>secret_instruction()</script><p>Hearing list</p><a href="/order.pdf">Order</a></html>')
        r=self.store.fetch('court','https://court.gov.in/info');page=self.store.read(r['document_id'])['pages'][0]
        self.assertIn('Hearing list',page['text']);self.assertNotIn('secret_instruction',page['text']);self.assertIsNone(page['pdf_page'])

    def test_corrupt_pdf_is_not_success(self):
        self.responses['https://court.gov.in/order.pdf']=(200,{'content-type':'application/pdf'},b'%PDF-1.4\nbroken')
        self.assertEqual(self.get()['status'],'extraction_failed')

    def test_normalized_empty_quote_rejected(self):
        r=self.get()
        for quote in (' '*8, '\u00ad'*8):
            with self.subTest(quote=quote),self.assertRaises(EvidenceError):
                self.store.check_quote(r['document_id'],quote,1)

    def test_repeated_fetch_does_not_overwrite_unrelated_hardlinked_file(self):
        import os
        r=self.get();target=Path(self.tmp.name)/'evidence'/r['document_id']/'document.bin'
        unrelated=Path(self.tmp.name)/'unrelated';unrelated.write_bytes(b'SYNTHETIC_UNRELATED')
        target.unlink();os.link(unrelated,target)
        self.assertEqual(self.get()['status'],'retrieved')
        self.assertEqual(unrelated.read_bytes(),b'SYNTHETIC_UNRELATED')

    def test_content_length_limit_keeps_size_status(self):
        from unittest.mock import patch,MagicMock
        import public_http
        response=MagicMock(status=200)
        response.getheaders.return_value=[('Content-Length','100')]
        connection=MagicMock();connection.getresponse.return_value=response
        with patch.object(public_http,'public_addresses',return_value=['8.8.8.8']),patch.object(public_http,'PinnedHTTPSConnection',return_value=connection):
            with self.assertRaises(FetchError) as error:
                public_http._request_once('https://court.gov.in/order.pdf',10,1)
        self.assertEqual(error.exception.status,'size_limit')
        response.read.assert_not_called()

    def test_overall_worker_timeout_includes_stalled_dns_or_reads(self):
        from unittest.mock import patch
        import public_http,time
        worker=Path(self.tmp.name)/'stalled.py'
        worker.write_text('import time; time.sleep(10)')
        started=time.monotonic()
        with patch.object(public_http,'__file__',str(worker)),self.assertRaises(FetchError) as error:
            public_http.request_once('https://court.gov.in/order.pdf',1000,0.15)
        self.assertLess(time.monotonic()-started,1.5)
        self.assertEqual(error.exception.status,'technical_failure')
