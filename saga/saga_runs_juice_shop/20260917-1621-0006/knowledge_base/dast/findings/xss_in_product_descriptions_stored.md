## Stored XSS in Product Descriptions

**Endpoint:** GET /api/Products
**Vulnerability Class:** Stored Cross-Site Scripting
**Evidence:** Product descriptions in the API response contain unescaped HTML tags.

### Detection Payload / Evidence
The following product descriptions contain unescaped HTML tags:

- Product ID 9 (O-Saft): `description` contains `<a href="https://www.owasp.org/index.php/O-Saft" target="_blank">More...</a>`
- Product ID 13 (Iron-Ons): `description` contains `<a href="...">iron-ons</a>`
- Product ID 17 (Temporary Tattoos): `description` contains `<a href="..."><code>@owasp_juiceshop</code></a>`
- Product ID 23 (Quince Juice): `description` contains `<em>Cydonia oblonga</em>`
- Product ID 24 (Apple Pomace): `description` contains `<a href="/recycle">sent back to us</a>`
- Product ID 32 (Pwning OWASP Juice Shop): `description` contains `<em>The official Companion Guide</em>` and `<a href="...">for free on LeanPub</a>`

### Impact
If an attacker can inject arbitrary HTML/JavaScript into product descriptions (via a write endpoint), stored XSS would occur when the API response is consumed by the frontend. The frontend renders these descriptions as HTML (not escaped), enabling script execution in the context of visitors viewing the product page.

### Technical Detail
The API returns raw HTML in the `description` field. The Angular frontend binds this data using innerHTML or similar unescaped binding, as evidenced by the presence of rendered HTML in the response body.

### Detection Method
Observed unescaped HTML tags in the `description` field of the `/api/Products` JSON response. No user-controlled input was needed for detection — the vulnerability is in how pre-existing content is stored and rendered.