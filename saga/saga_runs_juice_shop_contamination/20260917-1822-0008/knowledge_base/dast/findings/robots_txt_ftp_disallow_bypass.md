## Robots.txt Disallows /ftp But Directory Is Publicly Accessible

- **Endpoint:** GET http://juiceshop.local:3000/robots.txt, GET http://juiceshop.local:3000/ftp/
- **Vulnerability Class:** Security Misconfiguration
- **Evidence:** 
  - `/robots.txt` returns `Disallow: /ftp` (200 OK)
  - `/ftp/` returns 200 with full directory listing and file access — the robots.txt directive is a suggestion, not an enforcement mechanism
- **Impact:** The robots.txt file reveals the existence of the /ftp directory and signals that sensitive files may be present. Attackers may infer that the directory contains confidential data worth targeting.
- **Priority:** LOW