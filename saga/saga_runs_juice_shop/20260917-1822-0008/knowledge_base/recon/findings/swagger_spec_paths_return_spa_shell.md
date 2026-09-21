# Swagger/OpenAPI Spec Paths Return SPA Shell

## Test Results for Spec Discovery
| Path | Status | Content |
|------|--------|---------|
| `/api-docs.json` | 500 | Error: "Unexpected path: /api-docs.json" |
| `/swagger.json` | 200 | Angular SPA shell (not actual Swagger JSON) |
| `/swagger.yaml` | 200 | Angular SPA shell (not actual Swagger YAML) |
| `/openapi.json` | 200 | Angular SPA shell (not actual OpenAPI JSON) |
| `/openapi.yaml` | 200 | Angular SPA shell (not actual OpenAPI YAML) |

## Notes
- The only valid Swagger endpoint is `/api-docs` (Swagger UI HTML) and `/api-docs/swagger-ui-init.js` (embedded OpenAPI 3.0 spec)
- `/api-docs.json` returns a 500 error - the application does not serve this format
- Other common Swagger paths are caught by the Angular SPA router and return the application shell
- The B2B API spec is only available in the embedded JS file at `/api-docs/swagger-ui-init.js`