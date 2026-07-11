AttendEaseをAWS EC2にデプロイする（最新のmainブランチを反映）。

## 前提
- EC2キーペア: `~/.ssh/attendease-key2.pem`
- リージョン: `ap-southeast-2`
- **本番では必ず `docker-compose.prod.yml` を使う。** `docker-compose.yml`（開発用nuxt devモード）でフロントエンドを再作成すると "Vite Node IPC socket path not configured" エラーで500になる不具合があるため使用しないこと。

## 手順

1. EC2インスタンスの状態とパブリックIPを確認する。
   ```bash
   aws ec2 describe-instances --region ap-southeast-2 \
     --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name,IP:PublicIpAddress}' --output table
   ```
   - 停止していたら、起動してよいかユーザーに確認してから `aws ec2 start-instances` を実行する。
   - IPが前回と異なる場合は、後述の`.env`更新が必要になる（ユーザーに報告する）。

2. SSHで接続し、mainブランチを最新化する。
   ```bash
   ssh -i ~/.ssh/attendease-key2.pem ubuntu@<IP> "cd AttendEase && git fetch origin && git log HEAD..origin/main --oneline"
   ```
   - 新規コミットがあれば内容を確認してユーザーに報告してから `git pull origin main` を実行する。

3. ディスク容量を確認し、逼迫していれば事前に掃除する（ルートボリュームが6.7GBと小さく、"no space left on device" でビルド失敗しやすいため）。
   ```bash
   ssh -i ~/.ssh/attendease-key2.pem ubuntu@<IP> "df -h /"
   ```
   - 使用率が80%を超えていたら、ボリューム（`attendease_sqlite_data`）には触れずに以下を実行する。
   ```bash
   ssh -i ~/.ssh/attendease-key2.pem ubuntu@<IP> "docker builder prune -af && docker image prune -af"
   ```

4. 本番構成でビルド・起動する（時間がかかるためバックグラウンド実行し、完了通知を待つ）。
   ```bash
   ssh -i ~/.ssh/attendease-key2.pem ubuntu@<IP> "cd AttendEase && docker compose -f docker-compose.prod.yml up -d --build"
   ```
   - "no space left on device" で失敗した場合はステップ3のpruneを再実行してからリトライする。
   - もし開発用の `docker-compose.yml` で起動中のコンテナが残っていたら、先に `docker compose down`（開発用）で停止してから本番構成を起動する。

5. 動作確認する。
   ```bash
   ssh -i ~/.ssh/attendease-key2.pem ubuntu@<IP> "cd AttendEase && docker compose -f docker-compose.prod.yml ps"
   curl -sIL http://<IP>:3000 --max-time 10 | head -10
   curl -s -o /dev/null -w '%{http_code}\n' http://<IP>:8000/docs --max-time 10
   ```
   - フロントエンドは `/login` への302、バックエンドは200であることを確認する。

6. 結果をユーザーに報告する（反映されたコミット、フロントエンド/バックエンドのURL、ディスク使用率）。

## 注意事項
- `.env`の`NUXT_PUBLIC_API_BASE` / `CORS_ALLOW_ORIGINS`はEC2のIPアドレスに依存する。IPが変わっていた場合はこれらを更新してからビルドし直す。
- `attendease_sqlite_data`ボリュームは絶対に削除しない。破壊的なDocker操作（`down -v`等）を行う前は必ずユーザーに確認する。
- git pullで衝突やEC2側のローカル変更が検出された場合は、上書きせずユーザーに報告して指示を仰ぐ。
