# Cloudflare rollback

- Roll back Worker deployments using Cloudflare Workers deployment history or `wrangler versions` workflows.
- Roll back Container images by redeploying the previous git commit/image configuration.
- Database migrations must be backward compatible; destructive Alembic migrations are forbidden without an explicit recovery plan.
- Use Alembic downgrade only after validating data safety.
- Enable R2 object versioning/lifecycle policies for ledgers and keep previous import artifacts.
