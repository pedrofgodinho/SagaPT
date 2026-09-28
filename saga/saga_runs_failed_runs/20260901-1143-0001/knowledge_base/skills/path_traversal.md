# Path Traversal

Path traversal (directory traversal) occurs when user-controlled input is used to
build a filesystem path without proper sanitization, letting an attacker escape the
intended directory (e.g. via `../`) and read arbitrary files.

## Detection

Detection of path traversal is not currently in scope for the DAST agent — no
detection methodology is provided here. Exploitation begins from a path-traversal
finding confirmed elsewhere (a working traversal payload named in a finding).

## Exploitation

Prerequisites: a confirmed finding naming the vulnerable parameter and a working
traversal payload.

- Step 1 — Use the confirmed payload to read files with security impact:
  `/etc/passwd`, `/etc/shadow`, `.env`, `config.py`, `settings.py`, `secret_key`,
  `database.ini`.
- Step 2 — Read application source files if paths are inferable from recon findings.
- Step 3 — Extract credentials, secrets, or configuration that would enable further
  attacks.

Register: files read, their contents or relevant excerpts, and the security impact.
