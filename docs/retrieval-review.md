# Independent retrieval review — 2026-10-10

Reviewed `public_http.py`, `documents.py`, `retrieval.py`, `retrieval_server.py`, `tests/test_retrieval.py`, and the retrieval design dated 2026-10-10. Product and test files were read-only during this review. All reproductions used temporary synthetic evidence; no person, property, login, or evaluation files were inspected. This report records the implementation before the parent's subsequent fixes.

` .venv/bin/python -m unittest discover -s tests -v ` passed all 72 tests. These tests correctly reject wrong-page and fabricated quotations, private DNS answers, invalid origins, and simple cache corruption, but mostly inject an HTTP transport and therefore do not exercise the production response reader.

## Findings requiring fixes

### P1 — Existing hard links allow an evidence write outside its directory

`EvidenceStore.fetch`, `documents.py:195–200`, checks symlinks but then calls `write_bytes` on an existing file. A hard link is not a symlink. Refetching an unchanged document overwrites the linked inode and changes its permissions, affecting files outside the supplied evidence directory.

Reproduction with `RetrievalTests.setUp()` and its synthetic PDF transport:

```python
r = fixture.get()
p = fixture.store.directory / r['document_id'] / 'document.bin'
victim = Path(fixture.tmp.name) / 'synthetic-unrelated.txt'
victim.write_bytes(b'SYNTHETIC UNRELATED ORIGINAL')
p.unlink()
os.link(victim, p)
assert fixture.get()['status'] == 'retrieved'
assert victim.read_bytes().startswith(b'%PDF-')
```

Observed: the unrelated synthetic file was overwritten; link count was 2. The same issue applies to pages and metadata writes. This requires a preexisting link, not control of the remote public response or a race. Write fresh private temporary files and atomically replace cache entries instead of truncating existing paths; also consider directory replacement races separately.

### P2 — Empty normalized quotation reports an exact match

`documents.py:256–263` validates the original character count but not the normalized needle. Eight spaces and eight soft hyphens satisfy the length rule and normalize to an empty string. Python considers the empty string present in every page.

```python
r = fixture.get()
for quote in [' ' * 8, '\u00ad' * 8]:
    result = fixture.store.check_quote(r['document_id'], quote, 1)
    assert result['status'] == 'matched'
    assert result['matched_pdf_pages'] == [1, 2]
```

Both assertions reproduced. Reject an empty normalized quotation. Search queries containing only normalization-removed characters also produce meaningless matches and should receive the same validation.

### P2 — Retrieval wall-clock limit does not bound blocking DNS/body work

`public_http.py:73–75` performs DNS before starting its elapsed-time measurement. `response.read(65536)` at line 96 may perform many underlying socket reads, each receiving its own idle timeout; elapsed time is checked only after this blocking call returns. A server that continually trickles bytes within the idle timeout can retain the tool for much longer than the advertised total timeout.

Reproduction used a real `http.client.HTTPResponse` reading a synthetic socket pair, with immediate headers declaring an 8-byte body. The sending thread emitted one byte every 0.04 seconds. The receiving socket's timeout and `fetch_public` timeout were both 0.06 seconds. Patching only connection creation and DNS to attach this socket resulted in `FetchError('technical_failure', 'Document retrieval exceeded time limit')` after approximately **0.357 seconds**, nearly six times the configured limit. No real unapproved network connection was made. Larger bodies scale the delay further.

Apply an actual overall deadline to DNS, connection, headers, and body processing, with cancellation or a separately bounded worker where necessary. Check the deadline after transport returns as well. A socket idle timeout alone does not implement the design's bounded-time invariant.

### P2 — Production Content-Length oversize failures are mislabeled

`public_http.py:87–91` raises `FetchError('size_limit', ...)` inside a `try` caught by `except ValueError`. `FetchError` itself subclasses `ValueError`, so a valid oversized Content-Length is converted to `unexpected_content / Invalid response length`.

Reproduction patched `PinnedHTTPSConnection` with a response returning HTTP 200, `Content-Length: 100`, and `Content-Type: text/plain`, then called `request_once('https://court.gov.in/x', 10, 1)`. Observed `unexpected_content`, `Invalid response length`; the body was never read. Parse the integer inside the exception handler and compare its size afterward. Retain a production-reader test because the current injected-transport oversize test does not cover this branch.

## Evidence and limits

The production public transport successfully fetched `https://www.sci.gov.in/` (HTTP 200, text/html, 195,728 bytes) and `https://indiacode.gov.in/` (HTTP 200, text/html, 6,762 bytes) with eight-second requested limits. Neither request redirected, so this is actual public TLS/DNS evidence, not a live redirect demonstration. Redirect policy was reviewed in code and tested with synthetic transport responses. The connection uses the checked numeric address and validates TLS against the original hostname; no additional hostname DNS lookup is introduced in that connection path.

Raw/page hash checks reject ordinary single-file corruption. They are consistency checks against co-located mutable metadata, not authentication against a local writer who can alter pages and recompute `text_sha256`; retrieval time, warnings and extraction status likewise are not cryptographically protected. The existing no-signature limitation is appropriate, but documentation should avoid promising resistance to a hostile local cache writer.

PDF extraction runs in a subprocess with wall timeout, page/text bounds, and attempted CPU/data limits. This review verified the unit fixtures and inspected these controls; it did not certify memory behavior against decompression bombs or every supported OS's `resource` semantics. Static HTML is appropriately labeled as static rather than a completed interactive lookup. PDF indices, labels, and unspecified printed numbering are kept distinct. Quote responses expressly disclaim legal-holding, paragraph, case-identity and currentness verification.

SDK/package installation and wiring were being finalized independently and are outside this report. No legal-accuracy uplift, live PDF corpus coverage, consumer-host compatibility, or held-out evaluation result is established by this review.

## Independent follow-up after fixes — 2026-10-10

**Verdict: all four reported defects are resolved in the checked implementation.** Independently reran the full suite: 79 tests passed. No product files or evaluation outputs were inspected beyond the authorized retrieval code/tests, and no product files were edited.

- Both eight spaces and eight soft hyphens now raise `EvidenceError('Quotation contains no matchable text')` instead of returning `matched`.
- Repeated the hard-link reproduction separately for `document.bin`, `pages.json`, and `metadata.json`. Each refetch succeeded while preserving the unrelated synthetic file's bytes **and original 0644 permissions**. The private temporary-file plus `os.replace` implementation replaces the link instead of truncating its inode.
- Exercised the new production wrapper with a temporary child that imports the actual `_request_once`, connects it to a real synthetic `HTTPResponse`/socket pair, and trickles one byte every 0.08 seconds. The child's socket idle timeout was 0.15 seconds, so its internal read could otherwise continue. `request_once` terminated it with `technical_failure / Overall public HTTPS time limit reached; no record verified` after **0.155 seconds**, using a 0.15-second outer deadline. Code inspection confirms DNS/TLS/header/body work all occurs within this child. The added stalled-worker test also passed. `_request_once` alone retains an idle timeout, but the advertised production entry point now wraps it in a process deadline.
- Repeated the inner production Content-Length reproduction with a declared 100-byte body and 10-byte maximum. It now returns `size_limit / Document exceeds byte limit`, and never reads the body.

The original scope limits remain. The ancillary observation that a search query made only of soft hyphens can normalize to an empty query remains a low-impact input-validation improvement; it does not produce a quotation verification claim and is not one of the four blocking defects. Directory replacement races and a hostile writer able to rewrite both content and co-located hashes were not certified safe by these fixes.
