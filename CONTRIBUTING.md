# Contributing

Open an issue or pull request describing a concrete retrieval/workflow defect, with a minimal public example and expected/observed behavior. Omit client identities, private case details, credentials and downloaded matter files.

Source additions need an official publisher/inbound-link provenance record, operation-specific access assessment and review date. A government-looking domain, search snippet or directory entry does not establish current legal text or a completed lookup. API support needs documented permission/eligibility, a contract and tested operation support; private court-data vendors are outside this package's official-only policy.

For local checks, create a project Python3.10+ environment, install the pinned runtime dependencies listed in the scripts, run `python -m unittest discover -s tests -v`, then `python scripts/validate_package.py plugins/indian-law` and `python scripts/build_release.py`. The offline-only helper supports Python3.9+; PDF/MCP runtime needs Python3.10+.

Meaningful tests should cover behavior, not generated legal prose. Keep original bytes, viewer-page indices, printed pages, exact quotation checks and legal interpretation separate. Preserve observed failed retrievals and benchmark limitations; do not turn rubric points into accuracy percentages. Update shared version metadata together and validate extracted archives.
