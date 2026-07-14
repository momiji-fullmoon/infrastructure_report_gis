'use client';
import {useCallback, useEffect, useRef, useState} from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import {getJson, PondListResponse, PondSummary} from '../api';

type State='loading'|'ok'|'zero'|'network_error'|'http_error'|'invalid_json'|'timeout'|'outside_japan';
const JAPAN={west:122,south:20,east:154,north:46};
const defaultMapStyle={version:8 as const,sources:{osm:{type:'raster' as const,tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap'}},layers:[{id:'osm',type:'raster' as const,source:'osm'}]};
const mapStyle=process.env.NEXT_PUBLIC_MAP_STYLE_URL || defaultMapStyle;
export function clipJapan(bounds:{getWest():number;getSouth():number;getEast():number;getNorth():number}){
 const west=Math.max(bounds.getWest(),JAPAN.west); const south=Math.max(bounds.getSouth(),JAPAN.south); const east=Math.min(bounds.getEast(),JAPAN.east); const north=Math.min(bounds.getNorth(),JAPAN.north);
 if(west>east || south>north) return null; return {west,south,east,north};
}
export function popupDom(properties:any){
 const root=document.createElement('div'); const title=document.createElement('strong'); title.textContent=String(properties?.name ?? '名称未設定');
 const risk=document.createElement('span'); risk.textContent=`リスク:${String(properties?.risk ?? '未評価')}`; const quality=document.createElement('span'); quality.textContent=`品質:${String(properties?.quality ?? 'unknown')}`;
 const link=document.createElement('a'); const id=encodeURIComponent(String(properties?.id ?? '')); link.href=`/ponds/${id}`; link.textContent='詳細';
 root.append(title, document.createElement('br'), risk, document.createElement('br'), quality, document.createElement('br'), link); return root;
}
export function PondMap({initialItems=[]}:{initialItems?:PondSummary[]}){
 const mapRef=useRef<maplibregl.Map|null>(null); const divRef=useRef<HTMLDivElement|null>(null); const abortRef=useRef<AbortController|null>(null); const [items,setItems]=useState(initialItems); const [missing,setMissing]=useState(0); const [state,setState]=useState<State>('loading'); const [error,setError]=useState('');
 const toGeoJson=(ponds:PondSummary[])=>({type:'FeatureCollection' as const,features:ponds.filter(p=>p.location).map(p=>({type:'Feature' as const,geometry:p.location!,properties:{id:p.pondId,name:p.name,risk:p.risk?.riskLevel||'未評価',quality:p.coordinateQuality,flags:JSON.stringify(p.qualityFlags)}}))});
 const load=useCallback(async (bbox?:string)=>{abortRef.current?.abort(); const ctrl=new AbortController(); abortRef.current=ctrl; setState('loading'); try{const data=await getJson<PondListResponse>(`/ponds?limit=5000${bbox?`&bbox=${bbox}`:''}`,{signal:ctrl.signal,timeoutMs:10000}); setItems(data.items); setMissing(data.items.filter(p=>!p.location).length); setState(data.items.length?'ok':'zero'); const src=mapRef.current?.getSource('ponds') as maplibregl.GeoJSONSource|undefined; src?.setData(toGeoJson(data.items));}catch(e:any){if(ctrl.signal.aborted) return; setError(e?.message||String(e)); setState(e?.kind==='invalid_json'?'invalid_json':e?.kind==='timeout'?'timeout':e?.status?'http_error':'network_error');}},[]);
 useEffect(()=>{if(!divRef.current||mapRef.current) return; const map=new maplibregl.Map({container:divRef.current,style:mapStyle,center:[138,36],zoom:4}); mapRef.current=map; map.addControl(new maplibregl.NavigationControl()); map.on('error',ev=>{console.warn('MapLibre tile/style error', ev.error)}); map.on('load',()=>{map.addSource('ponds',{type:'geojson',data:toGeoJson(items),cluster:true,clusterRadius:50}); map.addLayer({id:'clusters',type:'circle',source:'ponds',filter:['has','point_count'],paint:{'circle-color':'#2563eb','circle-radius':['step',['get','point_count'],16,100,22,1000,30]}}); map.addLayer({id:'cluster-count',type:'symbol',source:'ponds',filter:['has','point_count'],layout:{'text-field':['get','point_count_abbreviated'],'text-size':12}}); map.addLayer({id:'pond-points',type:'circle',source:'ponds',filter:['!',['has','point_count']],paint:{'circle-color':['match',['get','risk'],'high','#dc2626','medium','#f59e0b','low','#16a34a','#64748b'],'circle-radius':7,'circle-stroke-width':1,'circle-stroke-color':'#fff'}}); map.on('click','pond-points',e=>{const f=e.features?.[0]; if(!f) return; const c=(f.geometry as any).coordinates; new maplibregl.Popup().setLngLat(c).setDOMContent(popupDom(f.properties)).addTo(map);}); load();}); let timer:any; map.on('moveend',()=>{clearTimeout(timer); timer=setTimeout(()=>{const clipped=clipJapan(map.getBounds()); if(!clipped){setState('outside_japan'); return;} load(`${clipped.west},${clipped.south},${clipped.east},${clipped.north}`);},350);}); return()=>{abortRef.current?.abort(); map.remove(); mapRef.current=null};},[load]);
 return <section><div className="mapLibre" data-testid="maplibre-map" ref={divRef}/><p><span className="pill">状態 {state}</span><span className="pill">表示 {items.filter(p=>p.location).length}件</span><span className="pill">座標欠損 {missing}件</span></p>{state!=='ok'&&state!=='loading'&&<div className="warn">{state}: {error || (state==='zero'?'検索条件に一致するため池は0件です。':'')}<button onClick={()=>load()}>再試行</button></div>}</section>;
}
