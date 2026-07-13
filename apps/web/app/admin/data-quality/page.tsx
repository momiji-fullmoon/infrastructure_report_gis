import {getJson} from '../../../src/api';
import {ErrorPanel} from '../../../src/ErrorPanel';
export default async function Page(){try{const data=await getJson<any>('/ponds?limit=100'); const missing=data.items.filter((p:any)=>!p.location).length;return <main className="card"><h1>データ品質</h1><p>0件時も明示: {data.count}件 / 座標欠損 {missing}件</p><div className="warn">品質問題と重複候補はフラグ表示し、自動統合しません。</div></main>}catch(e){return <main className="card"><ErrorPanel error={e} feature="データ品質"/></main>}}
