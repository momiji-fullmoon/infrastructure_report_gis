import {ApiError} from './api';
export default function ErrorPanel({error,feature,retryHref}:{error:unknown; feature:string; retryHref?:string}){const e=error as ApiError; return <div className="warn"><h2>{feature}を利用できません</h2><p>データ0件ではなくAPI接続に失敗しました。</p><p>Endpoint: {e.endpoint||'unknown'}</p><p>発生時刻: {e.occurredAt||new Date().toISOString()}</p><p>種別: {e.kind||'unknown'} / HTTP: {e.status??'n/a'} / Request ID: {e.requestId||'n/a'}</p><a role="button" href={retryHref||''}>再試行</a></div>}
export {ErrorPanel};
