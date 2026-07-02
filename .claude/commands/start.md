Docker 環境を起動する。

1. `/Users/aki/Desktop/AttendEase` に移動する
2. `docker compose up --build -d` を実行する
3. `docker compose logs --tail=30 backend` でバックエンドのログを確認し、`Application startup complete.` が出ているか確認する
4. `docker compose logs --tail=30 frontend` でフロントエンドのログを確認し、Nuxt の ready メッセージが出ているか確認する
5. 正常起動していれば以下を案内する：
   - フロントエンド: http://localhost:3000
   - バックエンド API ドキュメント: http://localhost:8000/docs
6. エラーがあればログを読んで原因を特定し、修正方法を提示する
