# First Cloudflare deploy

1. Provision managed PostgreSQL/PostGIS and verify TLS connection.
2. Set GitHub production Environment secrets.
3. Register API Worker secrets:
   ```bash
   cd deploy/cloudflare/api
   npx wrangler secret put DATABASE_URL
   npx wrangler secret put ADMIN_API_TOKEN
   ```
4. Run `.github/workflows/deploy-cloudflare.yml` manually.
5. Wait for API Container readiness using `/health/ready`.
6. Verify Web, API, proxy, map, and `/ponds` smoke checks.

Do not merge as fully deployed until real Cloudflare URLs have been checked.
