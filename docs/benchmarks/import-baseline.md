# Import baseline

現行実装は ORM `db.add()` を1件ずつ実行し、最後に一括コミットする構造だった。フル実行前にAlembic/PostGIS対応へ移行が必要だったため、ベースラインはコードレビューと小規模測定対象として記録する。

- コマンド: `python -m app.cli.import_ponds --input ../../tameike_ichiranR8.xlsx --limit 1000`
- 処理件数: 1,000件想定
- 成功/失敗: インポートCLIで集計
- rows/sec: 環境依存。ORM逐次addのため16万件フルは非現実的な可能性が高い
- ピークメモリ: 未計測だったため本変更で tracemalloc を追加
- 重複候補/欠損: プロセス内辞書依存だったためDB冪等性なし
- 再実行時追加件数: 一意制約なしのため重複登録リスクあり

再現コマンドはGit履歴の変更前実装で実行する。
