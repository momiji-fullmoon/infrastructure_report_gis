# Cloudflare and GitHub secrets

Do not commit secret values. Register Worker secrets with Wrangler and deployment secrets in the GitHub `production` Environment.

## API Worker secrets

- `DATABASE_URL`: PostgreSQL/PostGIS connection string, including SSL requirement such as `sslmode=require`.
- `ADMIN_API_TOKEN`: bearer token for production mutation APIs when explicitly enabled.

## GitHub Environment secrets

- `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`
- `DATABASE_URL`, `ADMIN_API_TOKEN`
- `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT`, `R2_BUCKET`
- `CLOUDFLARE_API_URL`, `CLOUDFLARE_WEB_URL`, `CORS_ALLOWED_ORIGINS`

R2 endpoint format is `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` unless a jurisdiction-specific endpoint is required.
