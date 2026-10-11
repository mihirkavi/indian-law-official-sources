# Source audit

Checked on 10 October 2026 using public web research. A page inspection is not an API/integration test. No client cases or property records were queried.

## Core and Maharashtra sources

| Source | Finding and intended use |
| --- | --- |
| [India Code legacy site](https://www.indiacode.nic.in/) | Inspected migration notice links to [indiacode.gov.in](https://indiacode.gov.in/). New endpoint opened but yielded no readable text through the tool. Discover individual Act documents at use time; do not assume complete current consolidation. |
| [e-SCR](https://scr.sci.gov.in/scrsearch/) | Inspected search interface; includes citation/keyword fields and CAPTCHA. The supplied “more than 1 million Supreme Court judgments” figure was not verified and will not be repeated. |
| [Supreme Court](https://www.sci.gov.in/) | Inspected official navigation to judgments, orders, rules, SCR, Verdict Finder, and [case status](https://www.sci.gov.in/case-status-case-no/). Prefer live navigation over the supplied legacy main.sci.gov.in URL. |
| [Judges Library](https://www.sci.gov.in/judges-library/) | Official page describes SUPLIS/LEGIS. Its old projected launch wording does not establish present availability of Vidhi Gyan Sampada. No promised integration or release date. |
| [eCourts](https://ecourts.gov.in/) and [Services](https://services.ecourts.gov.in/ecourtindia_v6/) | Root fetch failed; official service search results and [e-Committee documentation](https://ecommitteesci.gov.in/service/ecourts-services-mobile-application/) support case-status/order lookup. No authenticated or CAPTCHA lookup tested. |
| [NJDG](https://njdg.ecourts.gov.in/) | Official public search result inspected. Keep analytics distinct from judicial orders. The supplied 284 million total and court coverage counts were not verified. |
| [Central Gazette](https://egazette.gov.in/) | Root fetch failed; official indexed Gazette search/content pages found. Verify individual notifications and dates when researching. |
| [DoLR citizen services](https://dolr.gov.in/en/citizen-centric-services/) | Inspected official state/UT directory; use to discover revenue and registration sources. |
| [DILRMP dashboard](https://dilrmp.gov.in/) | Officially linked by DoLR. Programme statistics, not a nationwide parcel title search. Direct retrieval not tested. |
| [Bombay High Court](https://bombayhighcourt.gov.in/bhc/) | Inspected home page. [NIC order search](https://bombayhighcourt.nic.in/ord_qrywebcase.php) also surfaced in official results. Resolve current bench/service paths before case research. |
| [Maharashtra Act list](https://lj.maharashtra.gov.in/en/document-category/act-list/) | Inspected department index. Check each Act, amendment, rule, and date individually. |
| [Maharashtra Gazette gateway](https://dgps.maharashtra.gov.in/Site/Home/Index.aspx) | Official Directorate result and [state department description](https://industry.maharashtra.gov.in/en/allied-offices/directorate-government-printing-stationary-publication-mumbai) found. Gazette notices are distinct from historical district Gazetteers. |
| [Mahabhumi](https://mahabhumi.gov.in/) | Linked in DoLR directory. Root yielded an unexpected redirect/title and no usable text through the tool; individual services must be resolved before use. [Mahabhulekh](https://bhulekh.mahabhumi.gov.in/) is a supplied service candidate, not an integration tested here. |
| [IGR Maharashtra](https://igrmaharashtra.gov.in/) | Supplied official registration gateway; root fetch failed. Current department provenance and service endpoints still require verification before integration. |

## State portal inventory from the supplied list

These are routing candidates, not validated connectors. The DoLR directory confirms several publishers and supplies updated alternatives; directory links are not proof that every service currently functions.

| State | Supplied candidate | Directory update or status |
| --- | --- | --- |
| Uttar Pradesh | https://upbhulekh.gov.in/ | Listed by DoLR. |
| Maharashtra | https://bhulekh.mahabhumi.gov.in/ | Directory points to mahabhumi.gov.in. |
| Karnataka | https://landrecords.karnataka.gov.in/ | Directory points to rdservices.karnataka.gov.in. |
| Telangana | https://dharani.telangana.gov.in/ | Directory points to bhubharati.telangana.gov.in; official Bhu Bharati page inspected. |
| Madhya Pradesh | https://mpbhulekh.gov.in/ | Directory points to mpbhulekhrecords.com; verify official inbound provenance before use. Supplied “Kh those” text is malformed and omitted. |
| Rajasthan | https://apnakhata.rajasthan.gov.in/ | Directory points to apnakhata.raj.nic.in. |
| West Bengal | https://banglarbhumi.gov.in/ | Listed by DoLR. |
| Andhra Pradesh | https://meebhoomi.ap.gov.in/ | Listed by DoLR. |
| Bihar | https://biharbhumi.bihar.gov.in/ | Listed by DoLR. |
| Gujarat | https://anyror.gujarat.gov.in/ | Listed by DoLR. |
| Punjab | https://jamabandi.punjab.gov.in/ | Directory points to revenue.punjab.gov.in. |
| Haryana | https://jamabandi.nic.in/ | Listed by DoLR. |
| Tamil Nadu | https://eservices.tn.gov.in/ | Listed by DoLR. |
| Kerala | http://erekha.kerala.gov.in/ | Directory points to revenue.kerala.gov.in for RoR; survey archives are a separate record category. |

Additional supplied candidates: [IGRSUP](https://igrsup.gov.in/) and Karnataka Kaveri Online Services. These need current official department links before use; no Kaveri URL was supplied or guessed. Other states/UTs can be discovered through DoLR when needed.

## Excluded under the official-only requirement

The supplied SCC Online, Manupatra, Indian Kanoon, Taxmann/ITR, LII of India, and AIR Online are not government/judicial repositories. They will not serve as research or citation sources under the selected mode; no subscriptions or access connections are configured.

The supplied root-domain references to NUS LibGuides, LawCentral, Jurigram, Medium, Anantam IAS, landrecordsindia.com, Next IAS, and Assetly do not identify specific supporting documents and are not primary official authority. Google knowledge-panel/search links are also excluded. Supplied sci.gov.in and dolr.gov.in references have been replaced with relevant official pages above where found.

## Corrections to carry into the plugin

- Do not repeat unverified database size or coverage claims, or claim all Acts/orders/records are available.
- Follow current official migration/navigation links rather than freezing the supplied URLs.
- Separate revenue records and registered-document searches, and verify legal effects from applicable legislation and judgments.
- Record an access failure as a failure, not as absence of an Act, case, property, or liability.
- Library development announcements and older launch estimates do not prove a service is available today.

## API and authentication research added on 10 October 2026

- [Official PIB release](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=217906) describes NJDG API access for Central/State Government using departmental authorization. This is historical evidence of an API, not confirmation of current access for individual lawyers.
- [Official court-hosted technical presentation](https://cdnbbsr.s3waas.gov.in/s3ec0530a237d18c50f563cba4531f1db4/uploads/2024/02/2024022414.pdf) describes authorized eCourts APIs on Bharat API. Current onboarding, eligibility, endpoints, and limits still need verification before an adapter is enabled.
- [API Setu](https://apisetu.gov.in/) is an official API discovery gateway. Its existence does not prove a particular legal dataset is accessible; inspect actual provider listings and access terms.
- [Mahabhumi owner-search web-service description](https://ehakk.mahabhumi.gov.in/searchOwnerwebAPI/WebService1.asmx) was opened and advertises service operations. No owner query was sent. Approved third-party use, access requirements, limits, and completeness were not established.
- [Digitally signed Satbara](https://digitalsatbara.mahabhumi.gov.in/) indexed official page describes regular/OTP login for document downloads; direct opening yielded no readable content through the tool. Authentication must be checked for the specific service at runtime.
- [Aaple Abhilekh](https://aapleabhilekh.mahabhumi.gov.in/erecords/RegularSearch/RegularSearch) indexed official page displays sign-in. No login attempted.
- [IGR citizen registration](https://crm.igrmaharashtra.gov.in/citizen/Registration.html) confirms an account-related service exists. It does not establish that every IGR search requires login.

No API integration, authenticated session, or API entitlement was tested. API hostnames used for Supreme Court document files must not be treated as a documented public search API. API access supplied by a private court-data aggregator remains excluded under the official-only policy.

## Implementation follow-up: Maharashtra services

On 10 October 2026, inspected the official [Mahabhumi service gateway](https://mahabhumi.gov.in/mahabhumilink), the linked [Land Records Department services](https://bhumiabhilekh.maharashtra.gov.in/Services), and its [public View712 form](https://bhumiabhilekh.maharashtra.gov.in/Services/View712). The form expressly requests login when a digitally signed download is required. No parcel lookup, sign-in or paid download was performed. The [institutional registration page](https://bhumiabhilekh.maharashtra.gov.in/InstituteUser/Create) exposes institutional services/API onboarding; the linked API host timed out. A usable API contract, lawyer eligibility and credentials remain unverified. The [EODB page](https://bhumiabhilekh.maharashtra.gov.in/EODB) provides official inbound provenance for IGR Maharashtra. These links were added after the scored treatment run; source discovery metadata is not retroactive evidence for its answers.
