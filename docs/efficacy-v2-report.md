# Version 0.2 efficacy comparison — 2026-10-10

**One observed retrieval gain; no demonstrated legal-accuracy uplift or private-record access.** On three frozen prompts derived from the user's locality/family-law examples, the plugin context retrieved one relevant original judgment; both comparison contexts retrieved zero relevant case originals. All contexts tied on correctness/calibration and on two of three tasks. The independent assessor reproduced the decisive PDF and its exact byte hash.

## Results

| Human-selected topic | Ordinary AI, no plugin | Short official-source control | Plugin 0.2 |
| --- | ---: | ---: | ---: |
| Umerkhed property | 4/6; 0 case originals | 4/6; 0 | 4/6; 0 |
| Alibaug property | 4/6; 0 | 4/6; 0 | 6/6; 1 |
| Sangli/Yavatmal widow support or alimony | 4/6; 0 | 4/6; 0 | 4/6; 0 |
| Total | 12/18 | 12/18 | 14/18 |

These are predeclared rubric points, not accuracy percentages. Correctness/calibration was 6/6 in every arm. The two-point difference is one additional verified-record-evidence point and one completion/access point for Alibaug. No critical errors were established. No arm retrieved a local trial-court original, completed a local eCourts docket search, or produced an exhaustive list.

## Decisive original and access result

The plugin run found and downloaded the official Supreme Court judgment [Mohan Hirachand Shah v. Geeta Kumarchand Shah & Ors., 2024 INSC 222, 19 March 2024](https://api.sci.gov.in/supremecourt/2017/18931/18931_2017_14_1501_51594_FinalOrder_19-Mar-2024.pdf). Paragraph 2, page 2 identifies RCS103/1996 before the IInd Joint Civil Judge, Junior Division, Alibag. Paragraph 3 and pages 3–4 identify partition properties, including Mandve-Zirad/Dhokwade. Paragraph 28, page 24 records the appeals failing. The assessor independently downloaded the 25-page original (HTTP200, 422,996 bytes), matched the saved SHA-256, and checked those pinpoints. This is a Supreme Court original concerning local litigation; it is not a separately retrieved Alibag trial-court order or a current docket-status check.

The assessor's ordinary web open timed out; its direct public download succeeded. That demonstrates a useful second retrieval route. The record is publicly accessible and was found through an official-site search. It does not demonstrate access to a private or wholly unindexed record. Baseline/control were permitted to implement direct downloads and the baseline did so for other leads, so the plugin did not possess exclusive access. Query choices, source routing, reusable fetching, stochastic behavior and intermittent access are not isolated causal factors in this small comparison.

Umerkhed and the family topic remained unresolved in all arms. Inspected eCourts forms showed CAPTCHA and case/court filters; viewing these pages was correctly recorded as route evidence, not a completed case search. No CAPTCHA was bypassed, no account used and no private identifier lookup made. A missing date range, geographic/court scope and family-law category limit useful enumeration. A login prompt alone would not resolve these gaps. The control reported an inspected India Code HAMA original to clarify possible widow-support categories, but the assessor's repeat downloads timed out. That legislation is conditional evidence and contributes no local-case retrieval credit.

## Method and limits

The original human wording and clarification are retained in `eval/v2/user-questions.json`. Three prompts and rubric were frozen before answer runs. The human supplied broad topics, not identified legal cases, dates, private records or a lawyer-curated gold-answer set. Three fresh, independent contexts used the same inherited default model and ordinary tool environment; cases within each arm were handled as a batch. All were constrained to official sources and allowed ordinary public downloads. The short control added explicit original-document/citation/uncertainty instructions. Treatment additionally read the skill and could use its real packaged CLI; native MCP execution was not assumed or used.

Each task allowed at most ten external research actions, with one search/open/fetch per action, and answers at most 450 words. Actual counts were 29/29/30 for baseline/control/plugin. Local evidence reads, extraction and quotation checks were separate processing, not external retrieval. The parent checked trace counts and request structure (`compliance-audit.json`); it did not rewrite answers. Wall times and failures remain in raw traces; they are not a controlled latency benchmark.

An independent AI assessor received neutral labels, unedited answers and traces. Arm labels and some identifiers were removed, but helper names, route markers and differing trace structure remained identifiable. **This assessment is partially blinded, not fully blinded.** The assessor read no arm map, product, raw-arm folders or prior results. It verified the decisive record independently. AI assessment, one run per arm, broad prompts, no gold legal answers and volatile site access prevent statistical or general reliability claims. The baseline is ordinary AI under this test's official-source constraints, not the consumer ChatGPT product; Claude was not tested.

## Deliverable and remaining barriers

The new public-document engine supplies original bytes, origin/time/hashes, bounded extraction, stored page reads and normalized exact quote/page checks. Live SDK auto/legacy round trips exercised all four tools, and an installed Codex CLI fallback passed when public network access was enabled. Native MCP tools were not exposed inside this host; Claude integration remains untested. The engine does not supply restricted APIs, authentication entitlement, OCR, certified copies, private court records or automatic CAPTCHA completion. A legacy Bombay High Court nic.in lead was denied by the narrower configured public-fetch host; ordinary public fallback was attempted and timed out. Approved routes remain explicit rather than blanket government-domain trust.

The preserved version 0.1 benchmark still shows no benefit (46/48 baseline,45/48 control,45/48 plugin). Its archive hashes match the original release. The version 0.2 result shows one useful retrieval gain with material limits; neither comparison establishes that the plugin consistently gives more accurate legal answers.

## Reproducibility

Frozen inputs: `eval/v2/prompts.json` and `protocol.md`. Unedited answers/traces and original treatment bytes: `eval/v2/raw/`. Neutral copies/map: `blinded/` and `label-map.json`. Independent assessment and verification: `assessment.json`, `assessment.md`, `assessor-evidence/`. Mapped results: `results.json`. Technical integration evidence: `eval/v2/technical/` and `docs/retrieval-validation.md`. These development artifacts are excluded from the distributable plugin.
