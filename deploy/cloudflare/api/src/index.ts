import { Container } from '@cloudflare/containers';
import { env as workerEnv } from 'cloudflare:workers';

export interface Env {
  API_CONTAINER: DurableObjectNamespace<ApiContainer>;
  DATABASE_URL: string;
  ADMIN_API_TOKEN?: string;
  CORS_ALLOWED_ORIGINS: string;
  ALLOW_MUTATIONS: string;
}

const mutationMethods = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

function withSecurityHeaders(response: Response): Response {
  const headers = new Headers(response.headers);
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  headers.set('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'; base-uri 'none'");
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
}

export class ApiContainer extends Container {
  defaultPort = 8000;
  sleepAfter = '15m';
  envVars = {
    DATABASE_URL: workerEnv.DATABASE_URL,
    ALEMBIC_INI_PATH: '/app/alembic.ini',
    CORS_ALLOWED_ORIGINS: workerEnv.CORS_ALLOWED_ORIGINS,
    DEPLOYMENT_ENV: 'production',
  };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (mutationMethods.has(request.method) && env.ALLOW_MUTATIONS !== 'true') {
      return withSecurityHeaders(Response.json({ detail: 'Mutating API is disabled in production' }, { status: 403 }));
    }
    if (mutationMethods.has(request.method) && env.ALLOW_MUTATIONS === 'true') {
      const expected = env.ADMIN_API_TOKEN ? `Bearer ${env.ADMIN_API_TOKEN}` : undefined;
      if (!expected || request.headers.get('authorization') !== expected) {
        return withSecurityHeaders(Response.json({ detail: 'Unauthorized' }, { status: 401 }));
      }
    }
    try {
      const container = env.API_CONTAINER.getByName('primary');
      return withSecurityHeaders(await container.fetch(request));
    } catch {
      return withSecurityHeaders(Response.json({ detail: 'API container unavailable' }, { status: 503 }));
    }
  },
};
