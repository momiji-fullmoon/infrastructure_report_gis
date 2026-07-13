# Frontend API troubleshooting

- サーバー側URL: `API_INTERNAL_URL`（Dockerでは `http://api:8000`）
- ブラウザ側URL: `NEXT_PUBLIC_API_URL`（通常 `/api/backend`）
- Next.js rewrite: `/api/backend/:path* -> ${API_INTERNAL_URL}/:path*`
- FastAPI CORS: `CORS_ALLOWED_ORIGINS=http://localhost:3000`

画面はAPI停止、タイムアウト、4xx、5xx、不正JSON、0件を区別する。一般利用者へDBエラー全文やスタックトレースは表示しない。
