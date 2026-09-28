# SPA Hash Routes - No Server-Side Reflection

## Vulnerability Class
Information Disclosure / Client-Side Architecture

## Endpoint
All Angular SPA hash routes: `/`, `/#/login`, `/#/register`, `/#/admin`, `/#/basket`, `/#/product/1`, `/#/search`, `/#/privacy-security`, `/#/fraud`, `/#/contact`, `/#/data-export`, `/#/wallet`, `/#/order-history`, `/#/leaderboard`, `/#/recycling`, `/#/score-board`, `/#/admin/user-management`, `/#/admin/configuration`, `/#/admin/b2b`, `/#/jobs`, `/#/fileServer/ftp/acquisitions.md`

## Evidence
All 21 SPA pages return **identical HTML** (9393 bytes, same ETag `W/\"24b1-1a0aed3c5f2\"`). The server serves a static Angular shell for all hash routes - no hash-specific content is reflected server-side.

The HTML contains only:
- Copyright comment: `Copyright (c) 2014-2026 Bjoern Kimminich & the OWASP Juice Shop contributors. SPDX-License-Identifier: MIT`
- Cookie consent initialization with YouTube link: `https://www.youtube.com/watch?v=9PnbKL3wuH4`
- Angular Material theme CSS variables
- Script tags referencing: `polyfills.js`, `scripts.js`, `main.js`
- `<app-root></app-root>` placeholder

## Impact
No server-side XSS via hash route parameters. All routing is handled client-side by Angular. The Angular catch-all route in `/juice-shop/build/routes/angular.js:18` intercepts all `/rest/*` requests before they reach backend handlers, returning 500 errors with stack traces.

## Detection Payload
- `GET /#/search?q=<script>alert(1)</script>` → 200, identical static shell
- `GET /#/product/1?q=<script>alert(1)</script>` → 200, identical static shell
- `GET /#/<script>alert(1)</script>` → 200, identical static shell
- `GET /rest/product/search?q=<script>alert(1)</script>` → 500, Angular catch-all error