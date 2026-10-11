# Changelog

## 0.3.0 — 2026-10-11

- Added the `quashing-application` skill. It drafts a Bombay High Court (Nagpur Bench by default) Criminal Application (APL) under s.528 BNSS as an editable Word file.
- Bundled a house-format template derived from a practising advocate's filed sample, with all client details removed: A4, 2-inch top/left margins, Times New Roman 14 pt, double spacing, boxed cause title, numbered paragraphs, lettered grounds and prayers, solemn affirmation.
- Added a `uv` script (`build_apl.py`, pinned `python-docx==1.2.0`) that renders a JSON matter spec into the template. The script refuses to write inside the plugin and reports unresolved placeholders.
- Added references for the drafting style and an analysis/quality checklist. The checklist covers per-accused roles, offence ingredients, IPC-to-BNS temporal applicability, contradictions, witnesses and stage-appropriate interim relief.
- Added a list of authorities checked against official sources on 2026-10-11, with verification status.
- The validator now checks every bundled skill's frontmatter. The release adds a separate skill ZIP. Tests cover the template format and its placeholder-only content.
- Retrieval behaviour is unchanged.

## 0.2.2 — 2026-10-11

Verified native Claude Code use: a headless Claude Code 2.1.295 prompt invoked the skill and called `fetch_document`, `read_document` and `check_quote` to produce a quote-checked judgment brief. Documentation status updated accordingly. Retrieval behavior is unchanged.

## 0.2.1 — 2026-10-10

First public GitHub release. Adds a Claude marketplace description, installed-host demonstrations (native Codex MCP calls, native Claude Code MCP calls producing a quote-checked judgment brief), a public validation summary and documentation link/version regression tests. Also adds repository/author/license/discovery metadata, public installation instructions, curated validation and efficacy reports, CI, and an installed-plugin demonstration. Retrieval behavior is unchanged from 0.2.0; the earlier comparison applies to that recorded snapshot.

## 0.2.0 — 2026-10-10

Added bounded public HTTPS fetching, source-specific origin checks, static HTML/PDF extraction, saved-evidence hashes and timestamps, stored page reads and exact quotation/page checks. Added optional local stdio MCP tools and a CLI fallback, with pinned script dependencies. 79 tests passed; one public Alibag-origin judgment retrieval gain in the three-topic exploratory comparison. Native host MCP exposure and Claude invocation were not established.

## 0.1.0 — 2026-10-10

Initial portable official-source skill, source inventory, research/drafting/property/case workflows and configurable watchlist helpers. The eight-task comparison showed no accuracy benefit; results are preserved in the public report.
