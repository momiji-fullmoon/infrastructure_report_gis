import { NextRequest } from 'next/server';

const API = process.env.API_INTERNAL_URL || 'http://localhost:8000';
const forwardHeaders = ['accept', 'content-type', 'authorization', 'x-request-id', 'if-none-match'];
const responseHeaders = ['content-type', 'x-request-id', 'cache-control', 'etag'];

async function proxy(req: NextRequest, context: { params: { path: string[] } }) {
  const path = context.params.path.join('/');
  const url = `${API}/${path}${req.nextUrl.search}`;
  const headers = new Headers();
  for (const name of forwardHeaders) {
    const value = req.headers.get(name);
    if (value) headers.set(name, value);
  }
  const init: RequestInit = { method: req.method, headers, redirect: 'manual' };
  if (!['GET', 'HEAD'].includes(req.method)) init.body = await req.arrayBuffer();
  const res = await fetch(url, init);
  const out = new Headers();
  for (const name of responseHeaders) {
    const value = res.headers.get(name);
    if (value) out.set(name, value);
  }
  return new Response(req.method === 'HEAD' ? null : await res.arrayBuffer(), { status: res.status, headers: out });
}
export const GET = proxy; export const POST = proxy; export const PUT = proxy; export const PATCH = proxy; export const DELETE = proxy; export const HEAD = proxy; export const OPTIONS = proxy;
