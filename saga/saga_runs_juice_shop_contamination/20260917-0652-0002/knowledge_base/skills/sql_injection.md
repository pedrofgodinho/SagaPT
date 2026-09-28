# SQL Injection

SQL injection occurs when user-controlled input is concatenated into a SQL query
without proper parameterization, letting an attacker alter the query's structure.

## Detection

Goal: confirm that a parameter is injectable — not to extract data.

- Append a bare single quote `'` (or double quote `"`) followed by invalid SQL
  syntax to a parameter value and observe the response. A 500 error, a visible SQL
  error message (e.g. "syntax error", "unterminated quoted string",
  "ProgrammingError", "mysql_fetch"), or a structurally different response compared
  to a benign value is confirmed evidence of SQLi. For example, you may use
  `' trash` or `" trash` as a payload.
- Do NOT use `' OR 1=1 -- ` or similar "always-true" payloads as detection probes.
  In a search box they return all rows — the same result as an empty query — which
  is not distinguishable from normal behaviour and does not confirm a vulnerability.
- Try each candidate parameter separately so the trigger is unambiguous.
- Stopping point: a triggered SQL error confirms injectability, which is the
  detection goal. Do not proceed to ORDER BY, UNION SELECT, or information_schema
  queries — those belong to the Exploitation section below.

Record: endpoint, parameter name, the exact payload that triggered the error, and
the error text or anomaly observed. Note whether the error was a 500, a visible SQL
error, or a structurally different response — visible SQL errors are the strongest
evidence and should be flagged as higher priority.

## Exploitation

Prerequisites: a confirmed injection point naming the endpoint and vulnerable
parameter.

Goal: turn the confirmed injection point into real evidence of impact — recovered
schema, credentials, or other extracted data. There is no fixed sequence of steps;
read what each response tells you (identical vs. differing bodies, reflected values,
DB error text, timing) and let that evidence decide the next payload and technique.
Switch technique as soon as one stops producing new signal rather than persisting
with it.

Techniques — pick whichever fits the evidence, in no fixed order:

- **Error-based extraction** (e.g. MySQL `updatexml()` / `extractvalue()`;
  type-mismatch errors via `CAST()` / `CONVERT()` on other engines): forces the DB's
  own error message to contain injected data. Often the fastest path — it needs no
  column-count discovery and works even when nothing else is reflected in the
  response.
- **UNION-based extraction**: requires first finding the column count (`ORDER BY N`,
  or `UNION SELECT NULL,NULL,...` incrementing N) and a column position whose value
  is reflected back in the response. Cap column-count guessing at ~12 attempts — if
  nothing has resolved it by then, that approach isn't working; move to error-based
  or blind instead.
- **Boolean-based blind**: compare a TRUE vs. a FALSE condition's response
  (length/content) to extract data a bit or character at a time.
- **Time-based blind**: `SLEEP()` / `WAITFOR DELAY` / `pg_sleep()` and measure
  response latency, when nothing else differs.

**MySQL comment gotcha:** `--` needs a trailing space or control character to be
treated as a comment (`-- `, not `--`) — without it the query is left unterminated
and every attempt fails identically no matter what you vary. `#` is a safe
alternative if `-- ` still doesn't behave like a comment.

Register: the detection payload, which technique worked (and, briefly, what you
tried that didn't), the schema/data recovered, and enough request/response evidence
to reproduce it.
