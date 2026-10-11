# Watchlists and monitoring

Use [watchlist.json](../assets/watchlist.json) as a configuration template. `manual` is the default; it does not activate a schedule. Users choose case/statute/topic, identifiers, courts/jurisdiction, enabled official source IDs, languages, frequency/time, timezone, notifications/destination, and retention. Ask only for missing configuration required by the requested watch. Store configuration and matter data in the authorized workspace or host scheduler, never global memory.

Validate source IDs and capabilities. New official sources must first acquire provenance and an access assessment. Do not enable private sources. Credentials/session cookies are never part of a watchlist or baseline.

## Each check

Resolve the exact requested items using [access.md](access.md) and research/matter guidance. Record retrieval timestamp, source timestamp, document identity/version and meaningful content, not merely URL. An unchanged URL may serve a changed document. Use a document/content fingerprint or relevant verified fields when tools permit; never synthesize a fingerprint or treat missing fingerprint evidence as an unchanged document.

First successful observation establishes a baseline. Compare subsequent successful observations with the last successful baseline, reporting meaningful changes and the evidence. If any source is blocked, keep its baseline and mark it blocked; comparisons on successful sources may still proceed. No event found in a scoped successful search is narrower than universal absence of a legal change.

| Situation | Report |
| --- | --- |
| No earlier successful observation | Baseline established |
| Verified content/fields differ | Meaningful change, with before/after and evidence |
| Verified comparable content/fields same | No change observed within checked scope |
| Access failure, CAPTCHA, expired login or ambiguous identity | Unable to verify; preserve last successful baseline |
| Some sources succeed, others fail | Partial check; separate verified changes from gaps |

## Scheduling and notification

Create a recurring automation only when requested and the host exposes a supported scheduler. Name exact watch items, permitted sources, timezone, schedule and notification preferences. Confirm the scheduler's returned state before stating it is active. A portable JSON file or a promise in an answer is not an active background job. If the host cannot schedule, deliver a reusable manual check and say automation is unavailable here; no implicit cron/persistent service substitute.

Keep unchanged/non-actionable runs quiet unless the user requests periodic summaries. Notify on meaningful changes, retrieval failures or action needed according to configured preferences. Do not send externally through email/messaging without the user's chosen destination and explicit send authorization. Explain when the host cannot implement a requested notification setting rather than claiming it did.

Interactive login/CAPTCHA cannot be bypassed by a background run. Report one actionable barrier and request private login only if verified necessary; do not repeat the prompt on every retry/run when nothing has changed. Disclose that changing hosts may require reconfiguring the schedule and authentication. Pausing/deleting a monitor uses the host's actual management capability and requires a user request.

The [casework helper](../scripts/casework.py) can compare supplied successful observations and validate configurations; it does not fetch evidence, detect every legal change, or create schedules. A source observation must contain verified comparable content and a check timestamp before it can be classified unchanged.

Helper comparisons require a stable `item_id` for the specific case, statute, or topic as well as `source_id`. Different items on the same portal must never overwrite each other. Use an internal matter key without unnecessary personal data. Common credential keys are rejected, but this safeguard cannot detect all secrets embedded in free text; inspect inputs before supplying or storing them.
