# Broken Access Control & IDOR

Broken access control occurs when the application fails to enforce authorization,
letting a user reach resources or actions that should be denied. IDOR (Insecure
Direct Object Reference) is the most common form: the app hands you a reference to a
specific object and trusts you not to tamper with it.

## Detection

- After mapping authenticated resources (from recon findings), log out and attempt
  to access them directly; try accessing other users' resources by modifying IDs.
- Confirmed when a forbidden resource is returned (200 OK with actual content
  instead of a redirect or 403).
- Stopping point: retrieving a single object that isn't yours confirms the
  vulnerability — register it immediately (an IDOR you observed but never recorded is
  a lost finding). The exhaustive sweep to pull every record belongs to the
  Exploitation section below.

Test IDOR explicitly whenever an ID-like value is in play (and prioritise it if the
objective or a challenge hint points at IDs):

- Treat every ID-like value as a candidate, wherever it appears: numeric path
  segments (`/order/300123/receipt`), query-string params (`?id=42`), hidden form
  fields (`user_id`), JSON body fields, and cookies. The recon `attack_surface`
  finding usually lists them.
- Baseline first: request an object you legitimately own and note the shape of a
  *populated* response versus an *empty / not-found* one — these often BOTH return
  200, so distinguish them by body length and content, not by status code.
- Then change the reference to point at an object you should NOT see: another user's
  ID, and neighbouring values (±1, ±10, and a wider walk). Confirmed when you get
  back a *populated* response whose data belongs to someone other than your current
  session (or to no session).
- Do NOT conclude an ID parameter is "ignored" or inert from one or two adjacent
  values — the neighbours may simply not exist. A run of empty/not-found responses is
  NOT evidence the reference is safe; widen the sweep until you either retrieve one
  object that isn't yours or have covered a meaningful span. (Valid IDs are often
  sparse and non-contiguous, so ±1 alone routinely lands on gaps and tells you
  nothing.)
- Test the reference both authenticated (as a low-privilege user reaching another
  user's object) and unauthenticated (log out, then request it) — a resource that
  loads with no session at all is a missing-authorization IDOR and the strongest
  evidence.

Record: the resource URL, the user context (logged out / different user ID), and the
HTTP status + evidence that access was granted.

## Exploitation

Prerequisites: a confirmed accessible resource and the user context.

- Step 1 — Login as a legitimate user.
- Step 2 — Enumerate resources belonging to other users: iterate IDs, username
  slugs, or paths discovered in recon findings. Once access is confirmed for one, try
  up to 5 further identifiers — enough to demonstrate the pattern is systemic. Stop
  after 2-3 confirmed examples or 5 attempts, whichever comes first. Do NOT enumerate
  every possible ID.
- Step 3 — Try vertical escalation: access admin paths or privileged operations
  found by recon.
- Step 4 — Document all resources accessed and the data returned.

IDOR enumeration — turning a confirmed object reference into extracted data:

- The confirmed reference (e.g. `/order/<id>/receipt`, `?user_id=<n>`) is a window
  onto other users' objects. Sweep the reference space rather than probing single
  values: walk sequentially from a known-valid ID, and also probe larger steps,
  because valid IDs are often sparse and non-contiguous (e.g. 300123, 300214, 300327
  — gaps, not +1). Distinguish a populated response (another owner's real data) from
  an empty/not-found one by body content, not by status code — both commonly return
  200.
- Extract and record the contents of each out-of-scope object you reach. A hidden
  value inside another user's object — a credential, PII, or the specific target
  string the objective names (for a CTF, the flag) — is the impact evidence.
- When the objective is to locate ONE specific target object (a flag, a named
  victim's record, an admin's data) rather than to demonstrate a systemic pattern,
  the "stop after 2-3 / 5 attempts" cap in Step 2 does NOT apply: keep sweeping the
  reference space in sensible bounded passes until you retrieve that target object or
  exhaust a reasonable range.

Register: the list of accessed resources, data extracted from each, and the scope of
the breach.
