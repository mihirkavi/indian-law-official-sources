# Public validation scope

Last run: 10 October 2026, macOS, Python 3.12, `uv`, pypdf 6.20.0, MCP SDK 2.3.0. Earlier defect findings are in the [independent retrieval review](retrieval-review.md); raw development logs are retained privately.

## Hermetic checks (repeated in CI)

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 82 tests passed: package structure, access/watchlist helpers, guarded fetching, bounded transport, extraction, evidence integrity, quotation checks, documentation links and version consistency |
| `scripts/validate_package.py plugins/indian-law` | Passed (offline structure only) |
| `scripts/build_release.py` | Built plugin and skill archives and validated them after extraction; archives and hashes are attached to the GitHub release |

## Live public checks

These use ordinary public HTTPS downloads. Results reflect the sites on this date only.

| Check | Result |
| --- | --- |
| MCP stdio client using Claude Code's launch command (`uv run --script …/retrieval_server.py`) | Exposed `list_sources`, `fetch_document`, `read_document`, `check_quote`; 37 enabled sources |
| `fetch_document` on the MHA Bharatiya Nyaya Sanhita PDF | HTTP 200, no redirects, raw and text SHA-256 recorded |
| `check_quote` “THE BHARATIYA NYAYA SANHITA” on PDF page 1 and page 40 | `page_mismatch`, reporting actual page 2 |
| `check_quote` with absent text | `not_found`; no fuzzy repair |
| CLI fallback `check-quote` on PDF page 2 | `matched` |
| Complete judgment brief (Claude Code, CLI route); Codex native MCP; Claude Code plugin loading | See [installed demonstrations](installed-demo.md) |

## Not established

- A Claude Code session calling the plugin's MCP tools natively from a prompt (the standalone CLI was not signed in; loading and connection were verified separately).
- Legal accuracy, currentness, paragraph numbering, certified copies or exhaustive coverage.
- Availability of any site after this date, or any authenticated/CAPTCHA-protected service.
