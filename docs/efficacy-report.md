# Does the plugin improve legal answers?

**This experiment did not demonstrate an accuracy benefit.** The ordinary AI baseline scored **46/48**, the plugin **45/48**, and a supplementary short official-source instruction **45/48**. All three arms scored equally on substantive correctness and calibrated uncertainty. The small differences concern retrieved evidence, with both a plugin win and regressions. These are rubric points in one exploratory batch, not accuracy percentages or statistically significant effects.

The plugin ships as a reusable official-source workflow, source inventory, templates, and access/watchlist helper package. Its added structure is real, but an improvement in legal accuracy, retrieval success or reliability is not established by these results. It should not be promoted as more accurate than ChatGPT on this evidence.

## Method

Eight prompts were frozen before baseline/treatment runs in `eval/prompts.json`: BNS commencement, original mutation judgment, India Code migration, Maharashtra land-record authentication, a fabricated citation, BNSS transition, incomplete Marathi maintenance drafting, and a failed watch check without a scheduler. Both arms used fresh AI contexts, the same configured model/tool environment and a maximum of six web calls per case. Each context answered all eight prompts; cases are not eight independent model trials. Treatment loaded the packaged skill/references; baseline did not.

A third arm received only `eval/generic-control.md`, a short instruction to verify official originals, cite pinpoints and disclose gaps. It had no plugin source inventory or domain workflows. This supplementary control was added after the baseline finished and the author inspected two baseline answers; it was not part of the original two-arm preregistration. No hidden gold answers were supplied to the answer-producing agents.

An independent AI assessor saw unedited answers under labels randomized separately for each case. It read neither the identity map nor plugin/raw traces and verified decisive claims through official documents. Wording could reveal identity, so blinding is partial. Each answer was scored on substantive correctness, inspected official evidence/pinpoints, and calibration, each 0–2. Formatting, length and presence of a source ledger earned no accuracy points. The author then decoded labels and checked reported inspection against the saved traces without changing the assessor's scores.

## Results

| Arm | Correctness /16 | Evidence /16 | Calibration /16 | Total /48 | Web calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ordinary AI baseline | 16 | 14 | 16 | **46** | 25 |
| Short official-source instruction | 16 | 13 | 16 | **45** | 29 |
| Indian-law plugin | 16 | 13 | 16 | **45** | 26 |

| Task | Baseline /6 | Short instruction /6 | Plugin /6 |
| --- | ---: | ---: | ---: |
| Original BNS commencement | 6 | 6 | 6 |
| Original Jitendra Singh judgment | 5 | 4 | 4 |
| India Code migration | 6 | 6 | 6 |
| Preliminary/signed Maharashtra 7/12 access | 6 | 6 | 5 |
| Unverified citation / blanket bail claim | 6 | 6 | 6 |
| Pending-investigation transition | 6 | 6 | 6 |
| Marathi maintenance outline | 5 | 5 | 6 |
| Failed watch check / no scheduler | 6 | 6 | 6 |

Against baseline, the plugin won one case, lost two and tied five. Against the short instruction, it won one, lost one and tied six. No critical error was established in any arm. That means none was found in this narrow assessment, not that hallucinations or unsafe actions are eliminated. Token cost was not captured consistently, and trace timestamps do not support a controlled latency comparison; no cost/speed advantage is claimed.

## What the differences mean

The mutation task failed its central original-document requirement in every arm. Baseline inspected official corroborating judgments and disclosed that they were not the requested original, earning one partial evidence point. Plugin and generic arms had only indexed leads after failed downloads. The assessor could not reproduce the baseline's later PDF downloads; its one-point credit is conditional on the reported earlier inspection and saved trace. Official later quotations also use inconsistent paragraph numbering, so the evaluation does not certify an original pinpoint. The no-title proposition was corroborated through a [later Supreme Court judgment](https://api.sci.gov.in/supremecourt/2006/12193/12193_2006_9_1506_58088_Judgement_19-Dec-2024.pdf), paragraph 35; that is not the original requested decision.

For land access, baseline and generic inspected public viewing forms, while plugin disclosed that its public-form evidence was indexed after a failed retrieval. All identified the correct distinction between public viewing and signed authentication/payment. An alternate [official public form](https://bhulekh.mahabhumi.gov.in/NewBhulekh.aspx) and the [signed service](https://digitalsatbara.mahabhumi.gov.in/DSLR/Login/Login) were independently retrieved by the assessor. This is a retrieval regression, not an established wrong answer. No real plot, person, account or paid download was queried.

For the maintenance outline, plugin confined precise legal assertions to inspected BNSS text and kept other routes open. Baseline/generic supplied conditional HMA/DV section routes whose original texts were not fully retrieved; they disclosed that limitation, so their calibration remained full but evidence was partial. This favors narrower verified drafting, not a finding that their alternative routes were substantively wrong. The assessor confirmed BNSS sections 144–145 and the saving provision in the [official enactment](https://www.mha.gov.in/sites/default/files/2024-04/250884_2_english_01042024.pdf).

All arms handled the false citation, transition, commencement, migration and failed monitor appropriately. The baseline already did official research well under its ordinary host instructions. Most benefits may therefore come from basic good prompting and existing model/tool behavior, rather than the domain package. This run cannot attribute an independent causal advantage to the plugin.

## Practical value demonstrated separately

The deliverable standardizes a 56-entry inventory with source provenance/access/API assessments, evidence/draft/watchlist templates and reusable task routing. Its offline helpers passed 47 regression tests, including preserving blocked baselines, separating item identity, distinguishing 403 from login, restricting unverified sources and rejecting common credential keys. An installed Codex invocation read the skill and correctly answered the failed-monitor scenario. Three additional synthetic forward checks handled adversarial document instructions, unresolved conflicting judgments and partial monitoring results appropriately; see `eval/acceptance.md`.

These are usable functions and observed behaviors. They do not establish better substantive legal answers, tool-enforced official-only retrieval, exhaustive citator coverage, live authenticated record access or autonomous scheduling. A skill guides its host; it is not a complete security boundary or a database connector.

## Limits and next evidence needed

- One small, author-selected batch; no repeated trials, random allocation or matched live portal conditions. Tool access varied between runs. A one-point total difference is not a robust ranking.
- If baseline's provisional mutation evidence credit is removed, baseline and plugin tie at 45/48. Neither scoring choice establishes plugin uplift.
- AI author, answer agents and assessor; no practicing-lawyer review. The assessor saw answer disclosures, not a complete authenticated network log. Agent-written traces preserve URLs/failures/counts but are not an independent traffic audit.
- Some PDFs/portals failed for both answer agents and assessor. Original Jitendra Singh retrieval and numbering remain unresolved. Successful migration discovery does not prove legislation completeness or current consolidation.
- Marathi outline only; all-language accuracy was not tested. Consumer ChatGPT UI and Claude native behavior were not tested. Results concern this agent environment and cannot be generalized to those products.
- No real client matter, signed download, CAPTCHA bypass, institutional API entitlement or active scheduled watch was tested.
- Treatment file hashes are retained. Final release tightened helper/validator guards, added item-identity guidance and updated Maharashtra service/API-onboarding links after the treatment run. Those changes have regression and supplemental acceptance evidence; the numerical comparison was not rerun on the final release snapshot.

A stronger future comparison should use a lawyer-selected held-out matter set, repeated fresh runs on actual target hosts, stable/time-matched retrieval conditions, independent lawyer scoring and separate measures of original-document success, unsupported claims, currentness, user effort, cost and latency. A documented authorized retrieval connector could improve access, but no such API entitlement was available here and no adapter is claimed.

## Reproducible artifacts

- Frozen prompts/protocol/control: `eval/prompts.json`, `eval/protocol.md`, `eval/generic-control.md`.
- Unedited answers and traces: `eval/raw/baseline`, `eval/raw/generic`, `eval/raw/treatment`.
- Neutral bundles, assessor rationale and official-source access statuses: `eval/blinded`.
- Label map and decoded totals: `eval/label-map.json`, `eval/results.json`.
- Product verification/limitations: `docs/validation.md`, `docs/package-review.md`, `docs/acceptance-scenarios.md`.
