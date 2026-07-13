export const API=process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000';
export async function getJson(path:string){const r=await fetch(API+path,{cache:'no-store'}); if(!r.ok) throw new Error(path); return r.json()}
