export type RiskAssessment={assessmentId:string; pondId:string; assessedAt:string; hazard:number; vulnerability:number; exposure:number; anomaly:number; uncertainty:number; screeningScore:number; riskLevel:string; modelVersion:string; evidence:unknown};
export type PondSummary={pondId:string; name:string; prefecture?:string; municipality?:string; location?:{type:'Point'; coordinates:[number,number]}; coordinateQuality:string; qualityFlags:unknown; duplicateCandidate:boolean; dataSource:string; lastUpdatedAt:string; risk?:RiskAssessment};
export type PondListResponse={items:PondSummary[]; count:number; nextCursor?:number|null; total?:number; dataSource?:string; modelVersion?:string};
export type PondDetail=PondSummary;
export type DisasterEvent={eventId:string; name:string; eventType:string; occurredAt:string; status:string};
export type ApiHealth={status:string; database:string; postgis:string; satellite:string; simulation:string};
export class ApiError extends Error{status?:number; endpoint:string; requestId?:string; detail?:unknown; kind:string; occurredAt:string; constructor(message:string, endpoint:string, init:Partial<ApiError>={}){super(message); this.name='ApiError'; this.endpoint=endpoint; this.occurredAt=new Date().toISOString(); this.kind=init.kind||'api_error'; Object.assign(this, init);}}
export const browserBase=process.env.NEXT_PUBLIC_API_URL||'/api/backend';
export const serverBase=process.env.API_INTERNAL_URL||'http://localhost:8000';
export function apiBase(){return typeof window==='undefined'?serverBase:browserBase;}
export async function getJson<T=unknown>(path:string, opts:{timeoutMs?:number; signal?:AbortSignal}={}):Promise<T>{
 const endpoint=apiBase()+path; const ctrl=new AbortController(); const timeout=setTimeout(()=>ctrl.abort('timeout'), opts.timeoutMs??8000);
 if(opts.signal) opts.signal.addEventListener('abort',()=>ctrl.abort(opts.signal?.reason),{once:true});
 let r:Response; try{r=await fetch(endpoint,{cache:'no-store',signal:ctrl.signal});}catch(e:any){clearTimeout(timeout); throw new ApiError(e?.name==='AbortError'?'API request timed out or was aborted':'API connection failed', endpoint,{kind:e?.name==='AbortError'?'timeout':'network'});}
 clearTimeout(timeout); const requestId=r.headers.get('x-request-id')||undefined; const text=await r.text(); let body:any=null;
 if(text){try{body=JSON.parse(text);}catch{throw new ApiError('API returned invalid JSON', endpoint,{status:r.status,requestId,kind:'invalid_json',detail:text.slice(0,200)});}}
 if(!r.ok) throw new ApiError(`API returned HTTP ${r.status}`, endpoint,{status:r.status,requestId,kind:r.status>=500?'http_5xx':'http_4xx',detail:body});
 return body as T;
}
