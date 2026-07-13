import {getJson} from '../../src/api';
import {ErrorPanel} from '../../src/ErrorPanel';
export default async function Page(){try{const data=await getJson<any>('/disaster-events');return <main className="card"><h1>災害イベント</h1><p>{data.items.length}件</p><div className="warn">未接続データや解析失敗は実績として偽装しません。</div></main>}catch(e){return <main className="card"><ErrorPanel error={e} feature="災害イベント"/></main>}}
