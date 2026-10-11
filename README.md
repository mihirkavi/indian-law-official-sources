# Indian Law — Official Sources

[![CI](https://github.com/mihirkavi/indian-law-official-sources/actions/workflows/ci.yml/badge.svg)](https://github.com/mihirkavi/indian-law-official-sources/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A portable Agent Skill and public-evidence toolset for Indian lawyers, prioritizing **Maharashtra civil, criminal and family/domestic practice**. It works with compatible Codex and Claude Code plugin/Agent Skills hosts. The AI host supplies search, an interactive browser, interpretation, language ability and optional scheduling; this repository supplies legal research workflows, official-source routing, evidence tools and templates.

**Status: experimental, version 0.2.2.** Codex installation, native Codex MCP tool calls and the CLI fallback have been tested; a non-interactive Codex run correctly declined to brief when its approval policy blocked the tools. Claude Code 2.1.295 validates, installs and loads the plugin, and a headless Claude Code prompt called its MCP tools natively to produce a quote-checked judgment brief. See [installed demonstrations](docs/installed-demo.md). This is not a government product, certified legal database, filing service or a plugin that automatically works in every AI application.

## What it does

| Capability | Behavior |
| --- | --- |
| Official-source research | Use original government/judicial documents; retain links, dates, pinpoints, provenance and gaps. Exclude commercial/private legal databases and blogs. |
| Judgment briefs | Separate facts, issues, holdings, observations, relief and later-treatment limits; verify the original before claiming support. |
| Statute/version checks | Check amendments, commencement, section exceptions, repeal/savings and the law applicable on the relevant date. |
| Civil, criminal and family drafting | Prepare lawyer-reviewed outlines/drafts with material missing facts and placeholders; preserve jurisdiction and personal-law distinctions. |
| Case/status research | Route to the relevant official court/CNR service, disclose retrieval time and distinguish orders, registry entries and current status. |
| Property research | Distinguish RoR/mutation, registered deeds, encumbrances and title evidence; route to revenue/registration services. |
| Languages | Use the host's actual language ability, including Marathi/Hindi/English; label generated translations and preserve original identifiers. No every-language accuracy guarantee. |
| Configurable watchlists | User-selected cases/topics, timezone, frequency and notification settings. Manual by default; an actual supported host scheduler must confirm any recurring job. |
| Public evidence retrieval | Download approved public HTTPS documents, preserve original bytes/origin/time/hashes, extract static HTML/PDF text and read saved pages. |
| Exact quotation checks | Match normalized quotation text and viewer-page indices against saved extraction; reject wrong-page/absent text without fuzzy repair. This does not verify legal meaning or paragraph numbers. |

## Install

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) and make it available on the AI host's PATH if using the bundled public-evidence tools. The scripts have pinned dependencies and lockfiles; the first run can download Python/runtime packages. Retrieval/MCP require Python3.10+; the offline helper supports Python3.9+. The instruction-only skill still needs the host's own research tools.

### Codex

```sh
codex plugin marketplace add mihirkavi/indian-law-official-sources --ref v0.2.2
codex plugin add indian-law@indian-law-local
```

Invoke `indian-law` explicitly and refresh/restart the host if necessary. The marketplace identifier `indian-law-local` is retained for compatibility with earlier installations; it also identifies this public repository's catalog. Compatible Codex versions accept GitHub repository marketplace sources. Public GitHub availability does not mean listing in OpenAI's universal plugin directory.

### Claude Code

```text
/plugin marketplace add mihirkavi/indian-law-official-sources
/plugin install indian-law@indian-law-local
```

Then invoke the installed `indian-law` skill using the host's plugin command. These instructions target Claude Code, not a promise of Claude web support. Browser authentication and tool capabilities are client-specific. To try it without installing, start Claude Code with `claude --plugin-dir plugins/indian-law` from a checkout. A headless prompt-driven session with native MCP tool calls was verified.

### Local checkout or other Agent Skills hosts

```sh
git clone https://github.com/mihirkavi/indian-law-official-sources.git
cd indian-law-official-sources
codex plugin marketplace add .
codex plugin add indian-law@indian-law-local
```

For another compatible host, import `plugins/indian-law/skills/indian-law` into its documented skill location. The release's skill ZIP contains that directory. The full plugin ZIP contains portable, Codex and Claude manifests; repository marketplace installation uses the full checkout. Manual MCP setup uses the installed absolute path to `scripts/retrieval_server.py`; a shell-capable host can use the CLI when native MCP tools are absent.

## Try it

- “Use indian-law to research this Maharashtra civil issue under the law applicable on [date]. Verify original sources and adverse authority; give a memo with links and pinpoints.”
- “Brief [official judgment URL/citation]. Verify the caption, holding and relief, and disclose anything you cannot inspect.”
- “Which procedure applies to an investigation pending before 1 July 2024? Check commencement and savings before mapping sections.”
- “Prepare a Marathi maintenance-application outline. Clarify personal law, forum, relationships, income, children and existing proceedings.”
- “Look up this matter using [court/CNR/case number]. Report the observed status timestamp and available orders.”
- “Review these Maharashtra property documents and identify missing title-chain evidence.”
- “Configure my case/topic watchlist with my preferred schedule and notifications. Keep checks manual until a supported schedule is confirmed.”

Installed-plugin demonstrations are in [docs/installed-demo.md](docs/installed-demo.md). They are usability smoke tests on public URLs, not held-out efficacy comparisons.

## Sources, login and APIs

The [complete source inventory](plugins/indian-law/skills/indian-law/references/sources.json) records publisher, official provenance, current/legacy URLs, enabled/excluded status, access, API assessment and review date. The [source audit](docs/source-audit.md) explains unresolved candidates and corrections to unverified coverage claims. Inventory dates establish discovery review, not the current legal status of every document.

Sources include India Code; central/Maharashtra gazettes; Supreme Court/e-SCR/library; Bombay High Court; eCourts/NJDG; Maharashtra law/home departments; MHA; DoLR/DILRMP; Mahabhumi/registration services; and officially linked state land directories. Supplied private/open-access/commercial sources are explicitly excluded. Directory entries are routes, not validated live connectors or completed case searches.

**No authenticated official API adapter is enabled.** Prefer a documented official API only after contract, permission, eligibility and usable operations are verified. eCourts/NJDG describe restricted institutional access; usable lawyer-context entitlement was not established. Public PDF hosting on `api.sci.gov.in` is not a public judgment-search API. The bundled tool uses ordinary public HTTPS downloads.

Prompt for private sign-in only when the requested operation explicitly requires it, for example a signed land-record download. A CAPTCHA, fee, HTTP403, timeout or restricted API is not automatically a login requirement. Users enter passwords/OTP privately on the official service. Credentials and cookies are not handled by this public retrieval engine. Purchases, filing, registration changes and external messages require their own authorization.

## Public-evidence CLI and MCP

```sh
uv run --script plugins/indian-law/skills/indian-law/scripts/retrieval.py sources --store /absolute/matter/evidence
uv run --script plugins/indian-law/skills/indian-law/scripts/retrieval.py fetch --store /absolute/matter/evidence < request.json
```

Example `request.json` with an actual public MHA notification:

```json
{
  "source_id": "mha",
  "url": "https://www.mha.gov.in/sites/default/files/BhartiyaNyayaSanhita_24022024.pdf"
}
```

Commands are `sources`, `fetch`, `read` and `check-quote`. Optional stdio tools are `list_sources`, `fetch_document`, `read_document` and `check_quote`. All evidence operations require an explicit authorized directory. See [retrieval contracts and examples](plugins/indian-law/skills/indian-law/references/retrieval.md).

Downloads check source-specific HTTPS origins, redirects and public DNS destinations, with byte/time bounds. PDF extraction is subprocess-bounded; scans need another OCR workflow. Static HTML extraction does not execute JavaScript, submit a case search or complete CAPTCHA. A known official legacy host can still be outside a configured tool origin; verify provenance and use a supported public browser route rather than disabling origin checks.

Saved hashes detect inconsistency, not malicious replacement of both evidence and metadata. Viewer-page indices and PDF labels do not automatically identify printed pages. A quotation may be a submission or a quote of another case; inspect its context. No digital signature, certified copy, original case identity, legal holding, currentness, exhaustive citator coverage or title certification is guaranteed.

## Offline access and monitoring helper

```sh
python3 plugins/indian-law/skills/indian-law/scripts/casework.py access < observation.json
python3 plugins/indian-law/skills/indian-law/scripts/casework.py compare < comparison.json
python3 plugins/indian-law/skills/indian-law/scripts/casework.py validate-watchlist < watchlist.json
```

`access` classifies explicitly observed facts; it does not verify supplied flags. `compare` maintains separate source/item baselines and retains the last successful observation after failed checks; an unchanged URL does not prove unchanged content. The [monitoring guidance](plugins/indian-law/skills/indian-law/references/monitoring.md) and watchlist template explain inputs, timezone and notification settings. No scheduler is bundled and no live monitor was activated during development.

## Does it help?

The [version0.2 comparison](docs/efficacy-v2-report.md) used three frozen human-selected topics and the same model/tool environment:

| Arm | Rubric points | Verified relevant case originals |
| --- | ---: | ---: |
| Ordinary AI, no plugin | 12/18 | 0 |
| Short official-source instruction | 12/18 | 0 |
| Plugin0.2 | 14/18 | 1 |

The gain was a public Supreme Court original arising from an Alibag partition suit, independently downloaded and verified. Correctness/calibration tied. Umerkhed and Sangli/Yavatmal requests remained unresolved; no local trial-court originals or private records were retrieved. This small, partially blinded AI assessment is not evidence of generally better legal accuracy, consumer ChatGPT/Claude performance or privileged access. The [earlier eight-task comparison](docs/efficacy-report.md) showed no benefit. Versions 0.2.1 and 0.2.2 change publication metadata, documentation and host verification, not retrieval behavior.

Public evaluation material includes frozen prompts, unedited public-topic answers, curated action summaries, scores and assessor rationale under `eval/v2/`. Raw host sessions, downloaded records and user conversation text remain excluded; summaries are not full network logs.

## Development and validation

```sh
python3 -m venv .venv
.venv/bin/python -m pip install pypdf==6.20.0 mcp==2.3.0
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_package.py plugins/indian-law
.venv/bin/python scripts/build_release.py
```

**82 tests passed locally**. Checks cover package structure, access/watchlist behavior, guarded fetching, bounded transport, extraction, evidence integrity, exact/wrong-page/absent quotations, documentation links and version consistency. Four independently reviewed retrieval defects were repaired. Live public downloads and SDK stdio round trips passed; the installed Codex CLI fallback passed with network access. See [validation scope](docs/public-validation.md) and [independent retrieval review](docs/retrieval-review.md). CI repeats hermetic checks and archive validation; it does not certify legal accuracy or site availability.

[MCP SDK](https://py.sdk.modelcontextprotocol.io/), [Agent Plugins specification](https://agent-plugins.org/), [Codex packaging](https://developers.openai.com/plugins/build/plugins) and [Claude Code manifest documentation](https://code.claude.com/docs/en/plugins-reference) describe the underlying interfaces. Host/browser/scheduler capabilities and legal-source access may change.

## Data, license and support

Read [data handling](PRIVACY.md), [contribution guidance](CONTRIBUTING.md) and [changes](CHANGELOG.md). The package code and documentation are [MIT licensed](LICENSE); that license does not relicense linked government records, legal documents, third-party dependencies or trademarks. Government records are not bundled. A lawyer must review interpretations and drafts before use.

Maintained by [Mihir Kavishwar](https://github.com/mihirkavi). Report reproducible public examples through [GitHub issues](https://github.com/mihirkavi/indian-law-official-sources/issues), without client files, identifiers or credentials.
