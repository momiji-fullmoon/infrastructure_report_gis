# Tameike Resilience AI / Satellite PondWatch MVP Implementation Plan

## 1. 調査結果
- ルート直下に `openapi.yaml`、`database_schema.sql`、設計 docx、`tameike_ichiranR8.xlsx` が存在する。
- 既存アプリケーションコードは未配置のため、推奨構成に沿って `apps/api` と `apps/web` を新設する。
- `openapi.yaml` は PoC v0.9 で、ユーザー要求の追加API（災害イベント、リスク評価、推奨対応等）が含まれないため、MVPでは互換エンドポイントに加えて追加エンドポイントを実装する。
- `database_schema.sql` は主要テーブルの一部を定義済みだが、要件の全エンティティを満たすため Alembic 初期マイグレーションで不足テーブルを追加する。

## 2. 実装方針
1. Docker Compose、Makefile、`.env.example` によりローカル起動環境を整備する。
2. FastAPI + SQLAlchemy 2 + Alembic で API と DB モデルを実装する。
3. Excel ため池台帳インポート CLI を実装し、元値・正規化値・品質問題・重複候補を保存する。
4. 説明可能なベースラインリスク評価サービスを実装し、過去結果を上書きしない。
5. 衛星・シミュレーションは Provider インターフェースと mock/not_configured 実装に分離する。
6. Next.js で地図、ため池詳細、災害イベント、リスク、管理画面の垂直スライスを実装する。
7. pytest と Playwright の最小シナリオを追加する。
8. README に起動・運用手順、未接続範囲を明記する。

## 3. 垂直スライス順序
- ローカル起動環境 → DB → 台帳インポート → API → 地図画面 → リスク評価 → 災害イベント画面 → テスト → ドキュメント。

## 4. 主要な仮定
詳細は `docs/assumptions.md` に記録する。
