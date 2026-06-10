# AttendEase - 勤怠管理システム

小規模チーム（〜50人）向けの勤怠登録・管理アプリです。無料のOSS技術のみで構築しています。

> [!IMPORTANT]
> **複数ユーザーで同時に動作確認する場合は、異なるブラウザを使用してください。**
> 同一ブラウザでは複数タブを開いてもセッションが共有されるため、別ユーザーとしてログインできません。
> （例：管理者は Chrome、一般社員は Firefox、承認担当者は Safari）

---

## 機能

- 出退勤打刻（修正申請あり）
- 休暇申請・承認ワークフロー（有給残日数管理）
- 残業申請・承認ワークフロー（月次アラート）
- レポート・CSV出力

## ロール

| ロール | 権限 |
|--------|------|
| EMPLOYEE | 打刻・各種申請 |
| MANAGER | 部下の申請承認 |
| ADMIN | ユーザーアカウント管理・**新規ユーザー登録（ADMIN のみ可能）** |

> ユーザーの新規登録はシステム管理者（ADMIN）のみが行えます。一般社員・承認担当者は自己登録できません。

---

## 技術スタック

| 領域 | 技術 |
|------|------|
| フロントエンド | Vue 3 / Nuxt 3 / TypeScript / Tailwind CSS / Nuxt UI / Pinia |
| バックエンド | FastAPI / SQLAlchemy 2.0 / Alembic / python-jose / Pydantic v2 |
| データベース | SQLite 3 |
| インフラ | Docker / Docker Compose |

---

## 開発環境のセットアップ

### 必要なもの

- Docker
- Docker Compose

### 起動手順

**1. リポジトリをクローン**

```bash
git clone https://github.com/<your-username>/AttendEase.git
cd AttendEase
```

**2. 環境変数ファイルを作成**

```bash
cp .env.example .env
```

`.env` を開いて `JWT_SECRET_KEY` を任意の文字列に変更してください。

**3. Docker を起動**

```bash
docker compose up --build -d
```

**4. データベースの初期化**

```bash
# テーブル作成
docker compose exec backend alembic upgrade head

# テストユーザーの投入
docker compose exec backend python -m scripts.seed
```

**5. ブラウザでアクセス**

| URL | 説明 |
|-----|------|
| http://localhost:3000 | フロントエンド |
| http://localhost:8000/docs | バックエンド API ドキュメント |

### テストユーザー

| 社員ID | パスワード | ロール |
|--------|-----------|--------|
| ADMIN001 | Admin1234! | システム管理者 |
| EMP002 | NewPass456! | 承認担当者 |
| EMP001 | Password1! | 一般社員 |

> **複数ユーザーで同時に動作確認する場合は、異なるブラウザを使用してください。**
> 同一ブラウザではセッションが共有されるため、別ユーザーとしてログインできません。
>
> ブラウザの例：Google Chrome / Firefox / Safari / Microsoft Edge

### 停止・削除

**コンテナを停止する（データは保持）**

```bash
docker compose stop
```

**コンテナを停止して削除する（データは保持）**

```bash
docker compose down
```

**コンテナ・ボリューム・イメージをすべて削除する（データも消える）**

```bash
docker compose down --volumes --rmi all
```

> [!WARNING]
> `--volumes` を付けるとデータベースのデータも削除されます。再度 `alembic upgrade head` と `scripts.seed` の実行が必要です。

---

## 画面遷移図

```mermaid
flowchart LR
  %% ─── 認証エリア ───────────────────────────────────────────
  subgraph AUTH["🔐  認証"]
    direction TB
    Login("🏠 ログイン\n/login")
    PwReset("🔑 パスワードリセット\n/password-reset")
    Register("➕ ユーザー登録\n/register")
  end

  %% ─── 共通機能 ─────────────────────────────────────────────
  subgraph COMMON["👤  全ロール共通"]
    direction TB
    Dashboard("📊 ダッシュボード\n/")
    Attendance("🕐 出退勤打刻\n/attendance")
    Leaves("🌴 休暇申請\n/leaves")
    Overtime("⏰ 残業申請\n/overtime")
    Reports("📈 月次レポート\n/reports")
    Profile("⚙️ プロフィール\n/profile")
    Notif("🔔 通知\n/notifications")
  end

  %% ─── 承認担当者 ───────────────────────────────────────────
  subgraph MANAGER["✅  MANAGER / ADMIN"]
    direction TB
    LeaveApprove("✔️ 休暇申請承認\n/leaves/approve")
    OTApprove("✔️ 残業申請承認\n/overtime/approve")
  end

  %% ─── 管理者専用 ───────────────────────────────────────────
  subgraph ADMIN["🛡️  ADMIN 限定"]
    direction TB
    AdminUsers("👥 ユーザー管理\n/admin/users")
    AdminLeave("📋 有給残日数管理\n/admin/leave-balances")
  end

  %% ─── 遷移 ────────────────────────────────────────────────
  Login      -->|"✅ 認証成功"| Dashboard
  Login      -->|"❓ パスワード忘れ"| PwReset
  PwReset    -->|"完了"| Login
  AdminUsers -->|"新規作成"| Register

  Dashboard --> Attendance
  Dashboard --> Leaves
  Dashboard --> Overtime
  Dashboard --> Reports
  Dashboard --> Profile
  Dashboard --> Notif
  Dashboard -->|"MANAGER / ADMIN"| LeaveApprove
  Dashboard -->|"MANAGER / ADMIN"| OTApprove
  Dashboard -->|"ADMIN"| AdminUsers
  Dashboard -->|"ADMIN"| AdminLeave

  %% ─── スタイル ────────────────────────────────────────────
  classDef authStyle   fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,rx:8
  classDef commonStyle fill:#dcfce7,stroke:#22c55e,color:#14532d,rx:8
  classDef mgrStyle    fill:#fef9c3,stroke:#eab308,color:#713f12,rx:8
  classDef adminStyle  fill:#fce7f3,stroke:#ec4899,color:#831843,rx:8
  classDef hubStyle    fill:#f0fdf4,stroke:#16a34a,color:#14532d,font-weight:bold,rx:8

  class Login,PwReset,Register authStyle
  class Attendance,Leaves,Overtime,Reports,Profile,Notif commonStyle
  class Dashboard hubStyle
  class LeaveApprove,OTApprove mgrStyle
  class AdminUsers,AdminLeave adminStyle
```

---

## 画面モックアップ

### ログイン画面

```
┌─────────────────────────────────┐
│         AttendEase              │
│─────────────────────────────────│
│  社員ID    [__________________] │
│  パスワード[__________________] │
│                                 │
│      [ ログイン ]               │
│                                 │
│  パスワードをお忘れの方はこちら  │
└─────────────────────────────────┘
```

### パスワードリセット（2ステップ）

```
Step 1: 社員ID入力          Step 2: コード＋新パスワード入力
┌────────────────────┐     ┌────────────────────────────────┐
│ パスワードをリセット│     │ 新しいパスワードを設定          │
│────────────────────│     │────────────────────────────────│
│ 社員ID             │     │ ※ re***@example.com に送信済み │
│ [_______________]  │     │                                │
│                    │     │ 認証コード（6桁）               │
│ [ 認証コードを送信 ]│     │ [______]  有効期限: 10分       │
│                    │     │                                │
│ ログインに戻る     │     │ 新しいパスワード               │
└────────────────────┘     │ [____________________________] │
                           │ パスワード（確認）             │
                           │ [____________________________] │
                           │ [ パスワードをリセット ]       │
                           │ [ コードを再送信する ]         │
                           │ [ 戻る ]                      │
                           └────────────────────────────────┘
```

### ダッシュボード（打刻カード）

```
┌──────────────────────────────────────────────┐
│  AttendEase        🔔 通知  👤 山田太郎       │
│──────────────────────────────────────────────│
│  今日: 2026-06-06（土）                       │
│  ┌─────────────────────────────────────────┐ │
│  │  出社形態: ( 出社 ) / ( リモート )       │ │
│  │  出勤時刻: 09:00    退勤時刻: ──:──      │ │
│  │                                         │ │
│  │   [ 出勤打刻 ]      [ 退勤打刻 ]        │ │
│  └─────────────────────────────────────────┘ │
│  今月の勤務時間: 80h    有給残日数: 12日      │
└──────────────────────────────────────────────┘
```

---

## E-R 図

```mermaid
erDiagram
  users {
    int id PK
    string employee_id UK
    string name
    string email UK
    string hashed_password
    string role
    bool is_active
    int failed_login_count
    datetime created_at
    datetime updated_at
  }

  attendance_records {
    int id PK
    int user_id FK
    date date
    datetime clock_in
    datetime clock_out
    int break_minutes
    string status
    string work_type
    text correction_note
    datetime created_at
    datetime updated_at
  }

  leave_requests {
    int id PK
    int user_id FK
    int reviewer_id FK
    string leave_type
    date start_date
    date end_date
    int days
    text reason
    string status
    text reviewer_comment
    datetime reviewed_at
    datetime created_at
    datetime updated_at
  }

  overtime_requests {
    int id PK
    int user_id FK
    int reviewer_id FK
    date date
    datetime start_time
    datetime end_time
    int minutes
    text reason
    string status
    text reviewer_comment
    datetime reviewed_at
    datetime created_at
    datetime updated_at
  }

  leave_balances {
    int id PK
    int user_id FK
    int year
    int granted_days
    int used_days
    datetime created_at
    datetime updated_at
  }

  notifications {
    int id PK
    int user_id FK
    string type
    text message
    bool is_read
    datetime created_at
  }

  otp_codes {
    int id PK
    string employee_id
    string code
    datetime expires_at
    bool used
    datetime created_at
  }

  password_reset_tokens {
    int id PK
    string employee_id
    string code
    datetime expires_at
    bool used
    datetime created_at
  }

  users ||--o{ attendance_records : "打刻"
  users ||--o{ leave_requests : "申請"
  users ||--o{ overtime_requests : "申請"
  users ||--o{ leave_balances : "残日数"
  users ||--o{ notifications : "通知"
  users ||--o{ leave_requests : "承認"
  users ||--o{ overtime_requests : "承認"
```

---

## ブランチ運用ルール

- `main` ブランチへの直接 push は禁止しています
- 作業は `feature/xxx` などのブランチで行い、Pull Request を通してください

```bash
git checkout -b feature/your-branch-name
```
