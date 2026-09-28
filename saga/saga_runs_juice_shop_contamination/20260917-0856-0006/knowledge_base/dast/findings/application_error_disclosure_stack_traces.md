# Application Error Disclosure - Stack Traces

## Vulnerability Class
Information Disclosure

## Endpoint
Multiple endpoints return detailed stack traces on errors:
- `POST /api/Feedbacks/` (and `/api/Feedbacks`)
- `POST /rest/Feedbacks`
- `GET /api/captcha/`
- `GET /api/Feedbacks/1`

## Evidence
- `POST /api/Feedbacks/` with invalid payload returns 500 with full Express.js stack trace:
  ```
  Error: WHERE parameter "captchaId" has invalid "undefined" value
  at SQLiteQueryGenerator.whereItemQuery (/juice-shop/node_modules/sequelize/lib/dialects/abstract/query-generator.js:1770:13)
  at SQLiteQueryGenerator.whereItemsQuery (/juice-shop/node_modules/sequelize/lib/dialects/abstract/query-generator.js:1759:35)
  at SQLiteQueryGenerator.getWhereConditions (/juice-shop/node_modules/sequelize/lib/dialects/abstract/query-generator.js:2108:19)
  at SQLiteQueryGenerator.selectQuery (/juice-shop/node_modules/sequelize/lib/dialects/abstract/query-generator.js:1015:28)
  at SQLiteQueryInterface.select (/juice-shop/node_modules/sequelize/lib/sequelize/lib/query-interface.js:407:59)
  at Captcha.findAll (/juice-shop/node_modules/sequelize/lib/model.js:1140:47)
  at Captcha.findOne (/juice-shop/node_modules/sequelize/lib/model.js:1240:12)
  at async /juice-shop/build/routes/captcha.js:33:25
  ```
- `GET /api/Feedbacks/1` returns 401 with stack trace:
  ```
  UnauthorizedError: No Authorization header was found
  ```
- `POST /rest/Feedbacks` returns 500 with:
  ```
  Error: Unexpected path: /rest/Feedbacks
  at /juice-shop/build/routes/angular.js:18:18
  ```

## Impact
Stack traces reveal:
- Full server filesystem paths (`/juice-node_modules/sequelize/lib/...`)
- Framework versions (Express ^4.22.1, Sequelize ORM)
- Internal route structure (`/juice-shop/build/routes/captcha.js`)
- Database type (SQLite) and ORM internals
- Application architecture details

## Risk
Medium — Reveals application internals that aid targeted exploitation.