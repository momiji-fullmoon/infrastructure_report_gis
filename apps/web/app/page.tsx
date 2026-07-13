import {getJson, ApiHealth} from '../src/api';
import {ErrorPanel} from '../src/ErrorPanel';
export default async function Home(){try{const h=await getJson<ApiHealth>('/health');return <main className="card"><h1>全国ため池広域監視MVP</h1><p>API: {h.status} / DB: {h.database} / PostGIS: {h.postgis}</p><p><a href="/map">全国監視マップを開く</a> / <a href="/ponds">一覧</a></p></main>}catch(e){return <main className="card"><ErrorPanel error={e} feature="ダッシュボード"/></main>}}
