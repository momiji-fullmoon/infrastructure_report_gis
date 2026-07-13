# Assumptions

- PostgreSQL/PostGISを本番相当の基準とし、SQLiteは軽量単体テスト用途に限定する。
- 衛星Providerは未設定、シミュレーションProviderはサンプルモードとして明示する。
- `latitude` / `longitude` は移行期の互換カラムで、空間検索は `location` を正とする。
- フルインポートはローカル手動ベンチマーク対象で、通常CIでは小規模Excelを使う。
