Docker 環境を停止・削除する。

1. `/Users/aki/Desktop/AttendEase` に移動する
2. `docker compose down` を実行する
3. 停止・削除されたコンテナの一覧を確認して報告する

※ SQLite データ（sqlite_data ボリューム）は削除しません。
　 ボリュームごと削除したい場合は `docker compose down -v` を使用してください（実行前に確認を取ること）。
