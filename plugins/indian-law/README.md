# Indian Law — Official Sources

Version0.2.2: a portable Agent Skill and public-document evidence toolset for Indian lawyers, prioritizing Maharashtra civil, criminal and family/domestic practice.

Research and drafting use official government/judicial sources. The source inventory, access/API assessments, practice guidance, templates and configurable watchlist helpers are included in `skills/indian-law`. The CLI and optional local stdio MCP tools fetch approved public HTTPS documents, preserve origin/time/hashes, extract PDF/static HTML and check exact quotation/page matches.

Install through the public repository marketplace or import the skill into a compatible host. Public tools require `uv` on the host PATH (or Python3.10+ with pinned dependencies). The host supplies search, interactive browser, interpretation, language ability and optional scheduling. Public retrieval has no login credentials, restricted API entitlement, CAPTCHA solver or OCR; private sign-in is requested only when the actual operation requires it.

Codex installation, native Codex MCP calls and the CLI fallback passed live tests. A Claude Code prompt called the MCP tools natively and produced a quote-checked brief. The exploratory comparison found one public judgment retrieval gain, with correctness tied; no general accuracy or private-access improvement was established. A lawyer reviews interpretations/drafts. Exact text matches do not certify legal holdings, paragraph numbers or currentness.

[Full documentation, installation and evaluation](https://github.com/mihirkavi/indian-law-official-sources)

[Data handling](https://github.com/mihirkavi/indian-law-official-sources/blob/main/PRIVACY.md) · [Support](https://github.com/mihirkavi/indian-law-official-sources/issues) · [MIT license](LICENSE)

The license covers this package, not linked government records or third-party dependencies. No government affiliation is claimed.
