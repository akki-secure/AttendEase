# AttendEase - SKILL.md

このプロジェクトで作業するAI（Claude）が事前に知っておくべき技術知見・注意点をまとめたファイル。

## 技術スタック

- フロントエンド: Nuxt 3 (3.21.6) + Vue 3 + TypeScript + Tailwind CSS + Nuxt UI + Pinia
- バックエンド: FastAPI (Python 3.12) + SQLAlchemy 2.0 + Alembic + Pydantic v2
- データベース: SQLite（ファイルDB、Dockerの named volume `sqlite_data` に保存）
- インフラ: Docker + Docker Compose

## Docker操作の鉄則（最重要）

**named volume（`sqlite_data` など永続データ）を削除する操作は、実行前に必ずユーザーへ確認を取る。**

- `docker compose down -v` / `docker volume rm` は、フロントエンドの再起動・再ビルドが目的のときでも安易に使わない
- コンテナのトラブルシューティングは `docker compose restart` → `docker compose down`（`-v`なし）→ `docker compose build --no-cache` の順に、データを保持する範囲から試す
- `.claude/commands/down.md` にも同様の注意書きがある（`down -v` は実行前に確認を取ること）
- 2026-07-05、この鉄則を破ってDBデータ（ユーザーが独自に作成したアカウントを含む）を完全に失わせる事故を起こした。バックアップなしでの復元は不可能だった

## 既知のバグ・ハマりどころ

### 1. Nuxtの `ssr: false` + Vite Node IPCソケット未初期化バグ
`nuxt.config.ts` の `ssr: false`（SPA）構成で、開発サーバーが `Vite Node IPC socket path not configured` を出してクラッシュすることがある。これはNuxt本体の既知バグ（[nuxt/nuxt#34957](https://github.com/nuxt/nuxt/issues/34957)、Nuxt 4系では修正済みだが3.x系には未バックポート）。
**対応**: `ssr: true` に変更することで回避可能（このプロジェクトでは2026-07-05に適用済み）。

### 2. npmのoptionalDependencies解決の不安定さ
`package.json` の `"@nuxt/devtools": "latest"` のようにバージョン固定していない依存は、`npm install` のたびに解決結果が変わりうる。特にvite等のバージョンが意図せず変わり、`oxc-parser`（ネイティブバインディング）がプラットフォーム向けに正しく解決されない事例が発生した。
**教訓**: 固定バージョンを使う。lockfileはできるだけ `npm ci` で厳密に反映させる（ただし本プロジェクトのDockerfileは意図的に `npm install` を使用しているので、変更する場合は要検証）。

### 3. ホスト側の `.nuxt` / `node_modules` はエディタ用
Docker Composeでは `frontend/node_modules` と `frontend/.nuxt` を anonymous volume でコンテナ内に隔離しているため、実行時はホスト側にこれらが無くても問題ない。ただし**ローカルエディタ（VSCode等）のTypeScript解析用に、ホスト側にも `npm install` して `node_modules` と `.nuxt` を存在させる必要がある**（`.nuxt/tsconfig.json` が無いとエディタが `defineNuxtConfig` 等を解決できずエラーになる）。
- ホストで `.nuxt` を生成する際、Dockerコンテナと違うNode.jsバージョンで `npm install` すると `nuxt prepare` が失敗することがある。その場合は正常に動いているコンテナから `docker cp <container>:/app/.nuxt/. ./frontend/.nuxt` でコピーすればよい。
- `@types/node` を明示的に `devDependencies` に入れておくと `process` 関連のTS未解決エラーを防げる。

### 4. Docker Desktop起因のACL(deny delete)
`docker run -v <ホストパス>:/app ...` のようにホストディレクトリを直接bind mountしてコンテナ内(root)でファイル/ディレクトリを新規作成すると、Docker DesktopのファイルシステムがホストのACLに `deny delete` を付与し、ホスト側ユーザーが `rm`/`rmdir` できなくなることがある。
**対応**: `chmod -N <path>` でACLをクリアしてから削除する。

### 5. フロントエンドの品質チェックはコンテナ内で動かない
frontendコンテナのNode.jsバージョンが古く(`Object.groupBy is not a function`)、`eslint`・`vue-tsc`がコンテナ内では実行できない。**ホスト側のNode(v25系)で `npx eslint <path>` / `npx vue-tsc --noEmit` を実行すること。**

### 6. バックエンドのpytestはrequirements.txtに含まれない
`backend/requirements.txt`にはpytest等のテスト依存が含まれておらず、`tests/`配下にテストは存在するのに稼働中のbackendコンテナには入っていない。テスト実行時は都度 `docker exec attendease-backend-1 pip install --no-cache-dir pytest pytest-asyncio httpx` してから `python -m pytest -q` する(requirements.txtには追加しない運用)。

### 7. docker composeの`${VAR:-default}`は空文字も「未設定」扱い
`.env`で `NUXT_PUBLIC_API_BASE=`(空文字)と書いても、compose側が `${NUXT_PUBLIC_API_BASE:-/api}` のようにコロン付きデフォルトを使っていると、空文字は「未設定」とみなされデフォルト値が適用されてしまう。空文字を明示的に使わせたい場合は、compose側のデフォルト自体を空(`${VAR:-}`)にする必要がある。

## ジオフェンス機能のアーキテクチャ

- 拠点管理: `backend/app/models/office_location.py`(`OfficeLocation`)、機能ON/OFF: `backend/app/models/geofence_setting.py`(`GeofenceSetting`、単一行）。管理API・画面ともADMIN限定(`Depends(require_admin)` / `frontend/middleware/admin.ts`、MANAGERは不可)。
- 距離判定: `backend/app/core/geo.py` の `haversine_distance_meters` / `is_within_any_location`。
- 打刻時の判定: `backend/app/routers/attendance.py` の `_check_geofence()`。機能OFFまたは有効拠点0件なら無条件で素通り、位置情報未取得なら422、範囲外なら403。
- 打刻がジオフェンス判定を実際に通過したかどうかは `AttendanceRecord.clock_in_geofence_verified` / `clock_out_geofence_verified`(共にbool、マイグレーション`0016`)に保存され、`frontend/pages/attendance/index.vue` の勤怠一覧で「ジオフェンス」バッジとして表示される。
- HTTPS化(nginx + Let's Encrypt、本README「本番環境（HTTPS化）」参照)が無いと、ブラウザのGeolocation APIが動作せず本番では機能しない。

## シードデータ・テストアカウント

`backend/scripts/seed.py` で以下が作成される：
- `EMP001` / `Password1!`（EMPLOYEE、山田太郎）
- `EMP002` / `NewPass456!`（MANAGER、鈴木花子）
- `ADMIN001` / `Admin1234!`（ADMIN、システム管理者）

投入コマンド: `docker exec -w /app attendease-backend-1 python -m scripts.seed`

## 複数ユーザーでの同時動作確認

同一ブラウザでは複数タブを開いてもセッションが共有されるため、別ユーザーとしてログインできない。異なるブラウザ（Brave / Chrome / Safari等）を使うこと。

## 開発環境の起動・停止

`.claude/commands/start.md` / `down.md` を参照。基本的にはこれらの手順（`docker compose up --build -d` / `docker compose down`）を使う。
