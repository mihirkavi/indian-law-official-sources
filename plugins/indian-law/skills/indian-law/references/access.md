# APIs and access

Consult relevant entries in [sources.json](sources.json). `unverified` means no usable public contract/access has been established; it does not mean no API exists. `documented_restricted` and `candidate_unverified` cannot be called merely because a URL exists. `verified_available` requires documentation, eligibility, operation scope, auth method, and actual test evidence. All legal responses still need the original source/proposition verification.

## Retrieval selection

1. If a documented official API supports the requested operation, verify permission, current contract, and available entitlement. Prefer an authorized host API tool; add/use an adapter only from that contract. Respect documented pagination, scope, limits, and errors. An API hostname hosting PDFs is not a public search API.
2. If there is no usable API, use the appropriate official public search/page or direct document. Try a public route only when it provides the same requested record, not an uncertified substitute for a specifically requested certified copy.
3. If the requested record is only available through authentication, ask for user login to the verified official service. A separate restricted departmental API may require approval that a citizen login cannot supply.
4. If access remains blocked, say exactly which source/operation is blocked and offer manual retrieval of the official document. Record that it was not checked.

API discovery: follow official provider links and API Setu listings where relevant. Historical eCourts/NJDG documentation describes government departmental access; it does not establish individual lawyer access today. The Mahabhumi owner-search service description is a candidate, not permission to query owners. This release enables no unverified API adapter. Do not silently use eCourtsIndia or another private aggregator.

## Access states

| Observed condition | Next action |
| --- | --- |
| Public record accessible | Read it without requesting login |
| Explicit sign-in barrier for requested operation, with no equivalent public record | Request login once through that official service |
| Verified authenticated session expired | Request reauthentication once, then resume after access is observed |
| CAPTCHA | Ask user to complete it on the official page; no bypass |
| API requires an institutional entitlement not available | Explain eligibility barrier; use public records if suitable |
| Payment needed | Explain cost/barrier and stop paid operation until authorized; do other public work |
| Timeout, generic 401/403, malformed response, unexpected redirect | Diagnose boundedly; do not infer absence of a record or login requirement without supporting evidence |
| Successful official lookup explicitly returns no matching records | Report that exact lookup's result and scope, not universal non-existence |

Authentication prompt example: “The requested [operation] requires sign-in to [official service/link]. Please sign in directly there; keep your password and OTP private. I can resume after access is available.” Do not prompt for accounts speculatively or ask users to paste credentials, API keys, cookies, or tokens. Use supported host authentication or the user's already configured secret mechanism when a permitted API needs a secret.

After user login, check an observable authorized response/session. A message saying “done” without access is not a verified record. If this host cannot access the browser's authenticated session, state that and offer a downloaded official document; never imply the plugin shares sessions across hosts.

Stop retries after one reasonable alternate public route or one reauthentication request for the same barrier. Technical errors may be retried once if transient; avoid loops and expose remaining gaps. Background jobs cannot complete interactive login/CAPTCHA: mark blocked, retain the last successful baseline, and notify according to user settings.

Record `source_id`, requested operation, API/browser/direct-document/user-copy method, observed status, timestamp, exact document URL, and supporting evidence. Keep secrets and client identifiers out of operational logs. Login enables retrieval only; it does not authorize filing, purchase, registration, or changing records.
