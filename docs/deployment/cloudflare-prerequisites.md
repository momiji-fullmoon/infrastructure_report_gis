# Cloudflare prerequisites

- Cloudflare account with Workers Paid plan enabled for Containers.
- Docker capable of building `linux/amd64` images.
- Node.js 22 and npm.
- Wrangler from project dependencies.
- Managed PostgreSQL/PostGIS with TLS, backups, and a region suitable for Japan/Tokyo latency.
- Optional custom domain; workers.dev URLs can be used first.
- GitHub `production` Environment with reviewers/approval configured in repository settings.

## Official references checked

- Cloudflare Workers Next.js/OpenNext guide: https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/
- Cloudflare Containers getting started/configuration: https://developers.cloudflare.com/containers/get-started/
- Cloudflare Containers environment variables: https://developers.cloudflare.com/containers/platform/env-vars/
- Cloudflare R2 S3 API: https://developers.cloudflare.com/r2/api/s3/api/
- Cloudflare Workers GitHub Actions: https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/
- Cloudflare Wrangler configuration: https://developers.cloudflare.com/workers/wrangler/configuration/
