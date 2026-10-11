# Neutral-label v0.2 assessment

One answer retrieved a useful verified original: Alibaug C. All other answers accurately reported inability to retrieve a relevant local case, demonstrated an official search route and specified an actionable next step. They do not complete local record retrieval.

Scores follow the frozen rubric: correctness/calibration, verified relevant record evidence, completion/access, each 0–2. No formatting or ledger bonus applies.

| Case | Label | Correctness | Evidence | Completion | Total | Verified local-case-origin originals | Local trial-court originals | Portal interfaces | Legislation independently verified |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Umerkhed property | A | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |
| Umerkhed property | B | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |
| Umerkhed property | C | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |
| Alibaug property | A | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |
| Alibaug property | B | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |
| Alibaug property | C | 2 | 2 | 2 | 6 | 1 | 0 | 1 | 0 |
| Sangli/Yavatmal family | A | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |
| Sangli/Yavatmal family | B | 2 | 1 | 1 | 4 | 0 | 0 | 1 | 0 |
| Sangli/Yavatmal family | C | 2 | 1 | 1 | 4 | 0 | 0 | 2 | 0 |

Labels are per case; this report does not aggregate by arm or infer the hidden map.

## Independent verification and relevance

Alibaug C: independently downloaded the [official Supreme Court original](https://api.sci.gov.in/supremecourt/2017/18931/18931_2017_14_1501_51594_FinalOrder_19-Mar-2024.pdf), *Mohan Hirachand Shah v. Geeta Kumarchand Shah & Ors.*, Civil Appeals 773–775/2023, 2024 INSC 222, 19 March 2024. The 25-page PDF returned HTTP 200 and 422,996 bytes. SHA-256 `d8a4578825306ba932a65251aa3d70e479ca490ac9ebbf5adc11cd3fe21ba260` matches the neutral trace. Inspected caption/partition at page 1, paragraph 2/page 2 RCS 103/1996 before the IInd Joint Civil Judge, Junior Division, Alibag, paragraph 3/pages 3–4 schedule, paragraph 7/page 8 trial and first appeal, paragraph 28/page 24 sustaining the impugned judgment and dismissing the appeals, and page 25 date. It is a Supreme Court original about Alibag-origin property litigation, accurately described as such, rather than an independently obtained trial-court order. The answer does not claim property within the municipal town, a complete docket or current execution status. That disclosed scope suffices for 2/2/2.

The assessor reproduced the [eCourts CNR interface](https://services.ecourts.gov.in/ecourtindia_v6/), [Case Status interface](https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index) and [judgment search interface](https://judgments.ecourts.gov.in/pdfsearch/index.php). CNR/CAPTCHA and alternative case-status help, court selectors, Act/Case Type instructions, registration year and pending/disposed filters, and judgment keywords/CAPTCHA were present. These independently support one route-evidence point and one barrier/next-step point. No answer completed a local docket query. The three distinct interface URLs are not three concrete case records.

The family C answer claims inspection of the [Hindu Adoptions and Maintenance Act PDF](https://www.indiacode.nic.in/bitstream/123456789/1638/1/AA1956____78.pdf). Independent urllib, web open and curl attempts timed out; curl received zero bytes. Its statutory inspection remains conditional, not assessor-verified. Its summary carefully states applicability/factual uncertainty and distinguishes legislation from local cases; this source earns no extra local-record evidence or completion credit. No holding was accepted from a snippet.

## Rationale, failures and critical errors

Umerkhed A/B/C tie. A demonstrates CNR/Case Status interfaces; B marks WP 7778/2022 acquisition as an unverified taluka lead; C marks the Supreme Court cause-list lead as unverified and does not assume its dispute or outcome. All three distinguish town, taluka and court location, avoid claiming absence from empty searches, and supply scoped official next steps. No original property record was inspected.

Alibaug A/B tie below C. Both mark 2023:BHC-AS:24748 as an unverified lead. B also correctly warns that a court at Alibag does not establish an Alibaug property location for its other indexed lead. Timed-out High Court documents are not verified cases. C succeeds on a separately retrieved Supreme Court original; the earlier trial/High Court originals described there are not separately counted.

Family A/B/C tie. Each explains ambiguity between support after death and matrimonial maintenance/alimony without inventing personal law, relationships or entitlement. A marks its Sangli maintenance lead unverified and does not call it a widow case; B documents Case Status filters; C supplies conditional statutory context while explicitly disclaiming local-case retrieval. All correctly distinguish technical failures/CAPTCHA from an unsupported login demand.

No critical error is established in the nine final answers: no invented case/holding, nonlocal authority represented as a local original, directory represented as a searched docket, fabricated private access or unsupported login requirement. Assessor access intermittency is material: web opening the decisive Supreme Court PDF timed out while public download succeeded. Retrieval failure is not proof of absence or falsity.

## Blinding and interpretive limits

Only frozen prompts/protocol and nine neutral answer/trace pairs were read. The label map, raw arms, product, earlier evaluations/reports and other agents' work were not read. Blinding is partial: neutral traces retain `packaged_cli_fetch`, `actual_tool_route`, loaded-file manifest references and skill/context read names; answers mention a packaged helper. Trace schemas and detail also differ. Thus intervention characteristics may be apparent even without the map; the assessor did not infer arm identities for scoring.

This is AI assessment of three broad human-suggested topics, not an identified-case gold set or statistical study. One relevant published original, zero separately retrieved local trial-court originals, three unique portal interface URLs and one conditional legislation claim are the demonstrated evidence. Wins, ties and inability to retrieve cases must all be preserved. The results establish neither complete local coverage nor performance generalization to consumer ChatGPT or Claude. Parent trace-compliance analysis is separate from this substantive score.

Assessor-only verification downloads, extracted text, metadata and failures are in `eval/v2/assessor-evidence`; machine-readable per-case/label rationales are in `assessment.json`.
