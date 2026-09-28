## Information Disclosure - Unix Timestamp in Response Headers

- **Endpoint:** GET / (and other SPA routes)
- **Evidence:** ZAP detected Unix timestamps in the HTML response body (CSS variables containing values like `1666666667`, `1839622642`). These are likely build timestamps embedded in the application assets.
- **ZAP Alert:** Plugin 10096 "Timestamp Disclosure - Unix" (Low confidence)
- **Impact:** Timestamps can reveal application build/release dates, aiding attackers in identifying the software version and known vulnerabilities.
- **Risk:** Low
