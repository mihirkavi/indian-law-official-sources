"""Retrieve public official-origin evidence and check text; never certify legal conclusions."""
import datetime
import hashlib
from html.parser import HTMLParser
import json
import os
import tempfile
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import urljoin, urlsplit

from public_http import FetchError, MAX_BYTES, fetch_public, validate_url

MAX_PAGES = 400
MAX_TEXT = 3_000_000
ID_PATTERN = re.compile(r'^[a-f0-9]{64}$')
ACCEPTED_STATES = ('page_inspected','directory_linked','official_index_found')


class EvidenceError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalized(text):
    return ' '.join(unicodedata.normalize('NFKC',text).replace('\u00ad','').split()).casefold()


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.links, self.hidden = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript'):
            self.hidden += 1
        if self.hidden:
            return
        if tag == 'a':
            url = dict(attrs).get('href')
            if url:
                self.links.append(url)
        if tag in ('p','div','br','li','tr','h1','h2','h3','title'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script','style','noscript') and self.hidden:
            self.hidden -= 1
        if tag in ('p','div','li','tr','h1','h2','h3','title'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def pdf_worker(blob):
    """Runs only in a bounded subprocess. No OCR or printed-page inference."""
    import io
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU,(20,20))
        resource.setrlimit(resource.RLIMIT_DATA,(512*1024*1024,512*1024*1024))
    except (ImportError, ValueError, OSError):
        pass
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(blob))
    if reader.is_encrypted:
        raise EvidenceError('Encrypted PDF is unsupported')
    if len(reader.pages)>MAX_PAGES:
        raise EvidenceError('PDF page limit exceeded')
    labels = reader.page_labels
    pages, total, warnings = [], 0, []
    for index,page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ''
        except Exception:
            text = ''
            warnings.append(f'PDF page {index+1}: extraction failed')
        total += len(text)
        if total>MAX_TEXT:
            raise EvidenceError('Extracted text limit exceeded')
        if not text.strip():
            warnings.append(f'PDF page {index+1}: no extractable text; may be blank or need OCR')
        pages.append({'pdf_page':index+1,'pdf_label':labels[index],
                      'printed_page':None,'text':text})
    return {'pages':pages,'warnings':warnings}


def extract_pdf(blob):
    try:
        process = subprocess.run([sys.executable,str(Path(__file__).resolve()),'--extract-pdf'],
                                 input=blob,capture_output=True,timeout=30)
        if process.returncode or len(process.stdout)>MAX_TEXT*6:
            raise EvidenceError('PDF extraction failed or exceeded resource limits')
        result = json.loads(process.stdout)
        if not isinstance(result,dict) or not isinstance(result.get('pages'),list):
            raise EvidenceError('Invalid extraction result')
        return result
    except (subprocess.TimeoutExpired,ValueError,OSError):
        raise EvidenceError('PDF extraction failed or exceeded resource limits') from None


class EvidenceStore:
    def __init__(self,directory,registry,transport=None):
        directory = Path(directory).expanduser()
        if directory.is_symlink():
            raise EvidenceError('Evidence directory cannot be a symlink')
        self.directory = directory.resolve()
        self.registry, self.transport, self.max_bytes = registry, transport, MAX_BYTES

    def source(self,source_id):
        for source in self.registry.get('sources',[]):
            if (source.get('id')==source_id and source.get('enabled') is True
                    and source.get('official') is True and source.get('verification_status') in ACCEPTED_STATES):
                hosts = source.get('retrieval_hosts') or [urlsplit(source['url']).hostname]
                if not isinstance(hosts,list) or not all(isinstance(host,str) for host in hosts):
                    break
                return source,set(hosts)
        raise FetchError('blocked_origin','Source has no enabled verified-provenance retrieval route')

    def catalog(self):
        result = []
        for source in self.registry.get('sources',[]):
            try:
                row,hosts = self.source(source.get('id'))
            except FetchError:
                continue
            result.append({'source_id':row['id'],'publisher':row['publisher'],
                           'url':row['url'],'permitted_hosts':sorted(hosts),
                           'verification_status':row['verification_status']})
        return result

    def fetch(self,source_id,url):
        try:
            source,hosts = self.source(source_id)
            fetched = fetch_public(url,hosts,self.max_bytes,transport=self.transport)
        except FetchError as exc:
            # Reject URLs without echoing userinfo/query secrets from invalid input.
            return {'status':exc.status,'reason':exc.reason,'legal_holding_verified':False}
        except (OSError,ValueError,TypeError):
            return {'status':'technical_failure','reason':'Public retrieval failed; no record verified','legal_holding_verified':False}
        blob = fetched.pop('body')
        kind, warnings, links = None, [], []
        try:
            if blob.startswith(b'%PDF-'):
                kind = 'pdf'; extracted = extract_pdf(blob)
                pages,warnings = extracted['pages'],extracted['warnings']
            elif fetched['content_type']=='application/pdf' or urlsplit(fetched['final_url']).path.lower().endswith('.pdf'):
                return {'status':'unexpected_content','reason':'Requested PDF did not return PDF bytes','legal_holding_verified':False}
            elif fetched['content_type'] in ('text/html','text/plain','application/xhtml+xml'):
                kind = 'html' if fetched['content_type']!='text/plain' else 'text'
                text = blob.decode('utf-8',errors='replace')
                if kind == 'html':
                    parser = VisibleHTML(); parser.feed(text); text = ''.join(parser.parts)
                    for link in parser.links:
                        candidate = urljoin(fetched['final_url'],link)
                        try:
                            validate_url(candidate,hosts)
                        except FetchError:
                            continue
                        if candidate not in links:
                            links.append(candidate)
                        if len(links)>=100:
                            break
                    warnings.append('Static HTML text, not a rendered page or completed interactive lookup')
                if len(text)>MAX_TEXT:
                    raise EvidenceError('Text limit exceeded')
                pages = [{'pdf_page':None,'pdf_label':None,'printed_page':None,'text':text}]
            else:
                return {'status':'unexpected_content','reason':'Unsupported document type','legal_holding_verified':False}
        except (EvidenceError,ValueError,TypeError):
            return {'status':'extraction_failed','reason':'Document could not be extracted; use visual/manual inspection','legal_holding_verified':False}
        if not pages or not any(p['text'].strip() for p in pages):
            return {'status':'needs_ocr','reason':'No extractable text; original must be read visually/OCR','legal_holding_verified':False}
        raw_hash = digest(blob)
        document_id = digest((source_id+'\n'+fetched['final_url']+'\n'+raw_hash).encode())
        payload = json.dumps(pages,ensure_ascii=False).encode()
        metadata = dict(fetched,document_id=document_id,source_id=source_id,publisher=source['publisher'],
                        official_provenance_url=source['official_provenance_url'],
                        retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        sha256=raw_hash,text_sha256=digest(payload),kind=kind,page_count=len(pages),
                        extraction_complete=not any('PDF page' in w for w in warnings),warnings=warnings,
                        links=links,legal_holding_verified=False,
                        limitations=['Origin policy and content integrity are checked; no signature, case identity, printed-page numbering, legal holding, currentness or completeness is certified.'])
        try:
            target = self.directory/document_id
            target.mkdir(parents=True,exist_ok=True,mode=0o700)
            if target.is_symlink() or target.resolve().parent!=self.directory:
                raise EvidenceError('Invalid evidence location')
            for name,content in [('document.bin',blob),('pages.json',payload),('metadata.json',json.dumps(metadata,ensure_ascii=False,indent=2).encode())]:
                p = target/name
                if p.is_symlink():
                    raise EvidenceError('Invalid evidence file')
                with tempfile.NamedTemporaryFile(dir=target,delete=False) as temporary:
                    temporary.write(content)
                    temporary_name=temporary.name
                try:
                    os.replace(temporary_name,p)  # Replace a link itself; never truncate its target.
                    p.chmod(0o600)
                finally:
                    Path(temporary_name).unlink(missing_ok=True)
        except (OSError,EvidenceError):
            return {'status':'storage_failed','reason':'Cannot write evidence in configured local directory','legal_holding_verified':False}
        return dict(metadata,status='retrieved',preview=pages[0]['text'][:1800])

    def load(self,document_id):
        if not isinstance(document_id,str) or not ID_PATTERN.fullmatch(document_id):
            raise EvidenceError('Invalid evidence ID')
        target = self.directory/document_id
        try:
            if target.is_symlink() or target.resolve().parent!=self.directory:
                raise EvidenceError('Invalid evidence location')
            for name in ('document.bin','metadata.json','pages.json'):
                if (target/name).is_symlink():
                    raise EvidenceError('Invalid evidence file')
            if (target/'document.bin').stat().st_size>self.max_bytes or (target/'pages.json').stat().st_size>MAX_TEXT*6:
                raise EvidenceError('Evidence size limit exceeded')
            metadata = json.loads((target/'metadata.json').read_text())
            payload = (target/'pages.json').read_bytes();blob = (target/'document.bin').read_bytes()
            source,hosts = self.source(metadata['source_id'])
            validate_url(metadata['final_url'],hosts)
            expected = digest((source['id']+'\n'+metadata['final_url']+'\n'+digest(blob)).encode())
            if (metadata['document_id']!=document_id or expected!=document_id
                    or digest(blob)!=metadata['sha256'] or digest(payload)!=metadata['text_sha256']):
                raise EvidenceError('Evidence integrity check failed')
            pages = json.loads(payload)
            if not isinstance(pages,list) or len(pages)!=metadata['page_count']:
                raise EvidenceError('Invalid evidence pages')
            return metadata,pages
        except (OSError,KeyError,ValueError,TypeError):
            raise EvidenceError('Evidence is missing, corrupt or no longer permitted') from None

    def read(self,document_id,query=None,pdf_page=None):
        metadata,pages = self.load(document_id)
        if pdf_page is not None and (type(pdf_page)!=int or pdf_page<1):
            raise EvidenceError('PDF page must be a positive integer')
        if query is not None and (not isinstance(query,str) or len(query)>1000 or not query.strip()):
            raise EvidenceError('Use a nonempty bounded text query')
        selected = []
        for page in pages:
            if pdf_page is not None and page['pdf_page']!=pdf_page:
                continue
            text = page['text']
            if query:
                position = normalized(text).find(normalized(query))
                if position<0:
                    continue
                # Match occurs in normalized text; give context in that same representation.
                canonical = normalized(text)
                text = canonical[max(0,position-600):position+2400]
            selected.append(dict(page,text=text[:9000],truncated=len(text)>9000))
            if len(selected)>=5:
                break
        return {'document_id':document_id,'source':metadata,'pages':selected,
                'selection_limit':5,'scope':'Stored extraction from recorded time; not a fresh retrieval'}

    def check_quote(self,document_id,quote,pdf_page=None):
        if not isinstance(quote,str) or not 8<=len(quote)<=2000:
            raise EvidenceError('Quotation must be 8–2000 characters')
        if pdf_page is not None and (type(pdf_page)!=int or pdf_page<1):
            raise EvidenceError('PDF page must be a positive integer')
        metadata,pages = self.load(document_id)
        needle = normalized(quote)
        if not needle:
            raise EvidenceError('Quotation contains no matchable text')
        matched = [page['pdf_page'] for page in pages if needle in normalized(page['text'])]
        if pdf_page is not None and metadata['kind']!='pdf':
            raise EvidenceError('PDF page checking requires a PDF document')
        if not matched:
            status = 'not_found' if metadata['extraction_complete'] else 'incomplete_extraction'
        elif pdf_page is not None and pdf_page not in matched:
            status = 'page_mismatch'
        else:
            status = 'matched'
        return {'status':status,'document_id':document_id,'requested_pdf_page':pdf_page,
                'matched_pdf_pages':matched,'sha256':metadata['sha256'],'source_url':metadata['final_url'],
                'legal_holding_verified':False,'paragraph_number_verified':False,
                'normalization':'NFKC, soft-hyphen removal, whitespace collapse, casefold; no fuzzy matching',
                'limitations':'Text occurrence only; inspect caption/context and printed numbering. No legal applicability or currentness check.'}


if __name__=='__main__':
    if sys.argv[1:]==['--extract-pdf']:
        try:
            data = sys.stdin.buffer.read(MAX_BYTES+1)
            if len(data)>MAX_BYTES:
                raise EvidenceError('Byte limit exceeded')
            print(json.dumps(pdf_worker(data),ensure_ascii=False))
        except Exception:
            raise SystemExit(2)
    else:
        raise SystemExit('This module is used through retrieval.py or retrieval_server.py')
