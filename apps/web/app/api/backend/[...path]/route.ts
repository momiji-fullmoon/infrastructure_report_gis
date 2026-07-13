import {NextRequest} from 'next/server';
const API_INTERNAL_URL=process.env.API_INTERNAL_URL||'http://localhost:8000';
async function proxy(req:NextRequest,{params}:{params:Promise<{path:string[]}>}){const p=(await params).path.join('/'); const url=new URL(req.url); const target=`${API_INTERNAL_URL}/${p}${url.search}`; return fetch(target,{method:req.method,headers:{accept:req.headers.get('accept')||'application/json'},body:req.method==='GET'||req.method==='HEAD'?undefined:await req.arrayBuffer(),cache:'no-store'});}
export {proxy as GET, proxy as POST, proxy as PUT, proxy as DELETE};
