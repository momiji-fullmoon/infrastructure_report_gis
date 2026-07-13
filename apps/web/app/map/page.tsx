import {getJson, PondListResponse} from '../../src/api';
import {PondMap} from '../../src/components/PondMap';
import ErrorPanel from '../../src/ErrorPanel';
export default async function MapPage(){try{const data=await getJson<PondListResponse>('/ponds?limit=5000');return <main className="grid"><section className="card"><h1>全国監視マップ</h1><p>MapLibre GL JSで実座標を表示し、BBox連動検索します。</p><PondMap initialItems={data.items}/></section><aside className="card"><h2>サイドパネル</h2><p>リスクレベルとデータ品質を確認できます。</p></aside></main>}catch(e){return <main className="card"><ErrorPanel error={e} feature="監視マップ" retryHref="/map"/></main>}}
