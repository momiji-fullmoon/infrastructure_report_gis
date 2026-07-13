# Frontend/API troubleshooting

Browsers call `NEXT_PUBLIC_API_URL=/api/backend`; Next.js proxies to `API_INTERNAL_URL=http://api:8000` inside Docker. Error UI distinguishes loading, zero results, network/timeout, HTTP 4xx/5xx, and invalid JSON. Retry links reload the affected route, while the MapLibre component retries BBox requests in-place.
