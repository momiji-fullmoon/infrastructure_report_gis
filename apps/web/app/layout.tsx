import type {ReactNode} from 'react';
import './style.css';
export const metadata={title:'Satellite PondWatch'};
export default function RootLayout({children}:{children:ReactNode}){return <html lang="ja"><body><header><b>Tameike Resilience AI / Satellite PondWatch</b><nav><a href="/map">Map</a><a href="/ponds">Ponds</a><a href="/events">Events</a><a href="/risk">Risk</a><a href="/admin/data-quality">Data Quality</a></nav></header>{children}<footer>AI・衛星・シミュレーション未接続箇所は明示します。最終更新: MVP sample</footer></body></html>}
