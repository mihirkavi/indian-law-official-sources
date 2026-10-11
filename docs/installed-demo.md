# Installed-plugin demonstrations

These are host usability checks of the packaged plugin. They are not efficacy comparisons, and no client matters, credentials or private records were used.

## Codex 0.155.1 — native MCP calls (publication run, 10 October 2026)

Installed `indian-law@indian-law-local` 0.2.1. Prompt: brief a public Supreme Court order and verify it with the plugin's tools.

Observed in the event log (retained privately with other raw host sessions):

| Step | Result |
| --- | --- |
| Read installed `SKILL.md`, `retrieval.md`, `research.md`, judgment-brief template | Completed |
| Native MCP `list_sources` | Completed |
| Native MCP `fetch_document` (`sci`, `api.sci.gov.in/…/18931_2017_…_19-Mar-2024.pdf`) | Completed; HTTP 200 PDF saved with hashes |
| Native MCP `read_document` (query `Alibag`) | Completed. The saved page 1 extraction, read back afterwards, begins `2024 INSC 222` and Civil Appeal No(s). 773-775 of 2023 |
| Final brief | **Not produced**: the turn failed with “workspace is out of credits” |

This establishes that Codex can expose and call the plugin's MCP tools natively. It does not establish a completed brief or quote check from that run.

## Codex rerun (later on 10 October 2026)

The same request was repeated non-interactively with the default `approval_policy = never`. Codex read the skill and template, then `fetch_document` was refused: “MCP tool call requires approval, but approval policy is never.” The agent stated it could not verify the caption, date, bench, disposition or any quotation, and **did not write a brief from unverified material**, which is the intended behavior. A plugin-scoped `default_tools_approval_mode="approve"` override did not change the outcome in this Codex build. The interactive session below completed the brief with user-approved tool calls.

## Codex interactive session — completed judgment brief (11 October 2026)

Interactive Codex (`gpt-6-astra`, workspace-write sandbox with network access), plugin 0.2.2 installed from the local marketplace, same request and order. The user approved the plugin tool calls when prompted. At startup Codex reported that `indian-law-evidence` failed its first MCP handshake (“connection closed”). The server was then listed as starting again, and its tools were available for the turn. The cause of the first failure was not established; the same server answered `initialize` correctly when launched manually from Codex's plugin cache.

Codex natively called `fetch_document` once, `read_document` 7 times and `check_quote` once. It saved a 284-word brief that:

- verified the caption, 2024 INSC 222, C.A. Nos. 773–775 of 2023, the 19 March 2024 date and the Sundresh/Bhatti bench (PDF pp. 1, 25);
- correctly placed the challenge to items 19–21 at ¶9.1 (p. 12) and treated the exclusive-ownership argument at ¶12 as the appellant's submission, not the holding;
- quoted the operative order (¶28) with `check_quote` **matched** on PDF page 24;
- disclosed that later treatment, printed-page numbering, signature and certified-copy status were not verified.

Those pinpoints were independently re-read from the saved extraction. The brief itself and the session transcript are retained privately with the other raw host sessions.

## Claude Code session — completed judgment brief (CLI route)

A Claude Code (Opus 5.5) session followed the skill's `SKILL.md`, `references/retrieval.md` and `assets/judgment-brief.md`, using the documented shell route (`scripts/retrieval.py`) because the plugin's MCP tools weren't loaded in that session. Same public order as above. `fetch` returned HTTP 200, 25 pages, extraction complete, raw SHA-256 `d8a45788…ba260`, retrieved 2026-10-11 04:06 UTC. All 25 pages' text was read. `check-quote` matched every quotation below on the stated PDF page, which equals the printed page number for this document. A wrong-page control (page 25) returned `page_mismatch` and reported page 24.

> **Verified identity:** *Mohan Hirachand Shah v. Geeta Kumarchand Shah & Ors.*, Civil Appeal Nos. 773-775 of 2023, 2024 INSC 222 (non-reportable), Supreme Court of India, decided 19 March 2024. Bench: M. M. Sundresh and S.V.N. Bhatti, JJ.; judgment by Bhatti, J. (p. 1, p. 25).
>
> **Posture:** Partition suit RCS No. 103 of 1996 (Civil Judge J.D., Alibag), decreed 30.12.2005. Reversed in first appeal C.A. No. 56 of 2006 (District Judge, Raigad), 10.07.2006. The Bombay High Court disposed of S.A. Nos. 708/2008, 38/2009 and 386/2009 by common judgment of 21.03.2017. Defendant No. 1 appealed (paras 2, 7–8).
>
> **Issue:** Whether Defendant No. 1's alleged 1973 oral partition and supporting exhibits (Exs. 162, 196–198) defeat partition of items 19–21 (paras 20–22).
>
> **Holding:** The exhibits could not be relied on without adequate pleadings: “there is no room for any doubt on the inadequacy of pleadings on these crucial exhibits” (para 23.2, p. 21). There was no re-appreciation of evidence beyond Section 100 CPC: “We are in agreement with the findings recorded by the High Court.” (para 27.1, p. 24).
>
> **Relief:** “Therefore, the impugned judgment is sustained, and the Civil Appeals fail. No order as to costs.” (para 28, p. 24).
>
> **Distinguished:** Paras 6–6.3 record Defendant No. 1's pleaded case. The quotations at paras 23–24 are from earlier precedents, not this Court's own holding.
>
> **Not verified:** later treatment, review or curative proceedings; the High Court and trial-court originals; a certified copy. This is a public copy from `api.sci.gov.in` (registry source `sci`).

## Claude Code 2.1.295

Loaded for one session with `--plugin-dir plugins/indian-law` (no permanent install):

| Check | Result |
| --- | --- |
| `claude plugin validate .` and `claude plugin validate plugins/indian-law` | Passed. The only warning, a missing marketplace description, was fixed |
| `claude plugin list` | `indian-law@inline` 0.2.1 loaded |
| `claude mcp list` | `plugin:indian-law:indian-law-evidence` started via `uv run --script ${CLAUDE_PLUGIN_ROOT}/…/retrieval_server.py` and reported **Connected**, including from a path containing spaces |
| Headless prompt (`claude -p --plugin-dir …`), after CLI sign-in | **Passed**: invoked skill `indian-law:indian-law`, read the brief template, then natively called `fetch_document`, `read_document` (4 times) and `check_quote` on the same Supreme Court order. Produced a brief with verified caption, date, bench and disposition. The operative order in para 28 was quote-checked as `matched` on PDF page 24. The brief disclosed that pages 4–23 were unread, and that it had not verified certification, later treatment or the diary-number mapping. 11 turns |

Only the listed tools were permitted for that run. The identical stdio launch command was also driven by an MCP SDK client; see [public validation](public-validation.md).
