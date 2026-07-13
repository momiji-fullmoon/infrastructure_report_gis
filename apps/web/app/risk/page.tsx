import {getJson} from '../../src/api';
import {ErrorPanel} from '../../src/ErrorPanel';
export default async function Page(){try{const data=await getJson<any>('/ponds?limit=100');return <main className="card"><h1>リスクランキング</h1><p>{data.count}件</p>{data.items.map((p:any)=><p key={p.pondId}>{p.name}: {p.risk?.riskLevel||'未評価'}</p>)}</main>}catch(e){return <main className="card"><ErrorPanel error={e} feature="リスク"/></main>}}
