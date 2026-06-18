# AttendEase - 勤怠管理システム

小規模チーム（〜50人）向けの勤怠登録・管理アプリです。無料のOSS技術のみで構築しています。

> [!IMPORTANT]
> **複数ユーザーで同時に動作確認する場合は、異なるブラウザを使用してください。**
> 同一ブラウザでは複数タブを開いてもセッションが共有されるため、別ユーザーとしてログインできません。
> （例：管理者はBrave 、一般社員は Google Chrome、承認担当者は Safariの中のGoogleChrome）

---
## AttendEase(勤怠管理システム)の流れ
1.「http://localhost:3000/login」にアクセスすると「ログイン画面」が、表示されます。




<img width="647" height="567" alt="スクリーンショット 2026-06-10 20 53 01" src="https://github.com/user-attachments/assets/62bdd3c4-bfa1-4c42-a57a-6fb16f05c159" />





2.一般社員:新規ログインする場合は、新規登録をクリックしてください。新規登録の完了を登録をする前に、必ず、「社員ID」と「パスワード」はメモするようにお願いします。新規アカウントに必要な「社員ID」、「氏名」、「メールアドレス」、「パスワード」を入力して、「登録」をクリックして完了するとログイン画面に戻り、新規アカウントの作成が完了しました。





<img width="647" height="603" alt="スクリーンショット 2026-06-10 20 56 01" src="https://github.com/user-attachments/assets/28d5007c-bba1-4bdc-8210-59e8f93899bc" />



⚠️既存のアカウントで、正しいユーザーIDとパスワードを入力に「３回失敗」すると「アカウントロックになりますので、ご注意ください。







<img width="486" height="604" alt="スクリーンショット 2026-06-14 18 33 49" src="https://github.com/user-attachments/assets/40fe3091-e631-4a83-8667-e8a75e3b76c1" />




















3.一般社員:新規アカウントで作成したユーザーIDとパスワードを入力後、「次へ進む」をクリックしてください。







<img width="647" height="603" alt="スクリーンショット 2026-06-10 21 10 50" src="https://github.com/user-attachments/assets/bd626dd7-8b58-45f3-a70a-21fe0e562f80" />











※間違った社員IDまたはパスワードを入力してログインしますと、「社員IDまたはパスワードが正しくありません」とエラーが表示されますので、ご注意ください。




<img width="647" height="603" alt="スクリーンショット 2026-06-10 21 08 40" src="https://github.com/user-attachments/assets/f35ce9e7-1a7d-481d-89b4-d4d7cb8b16a9" />







4. 一般社員:「認証コード」を認証コードのフォームに入力して、ログインしてください。※もし、時間内に入力できない場合は、「再送信」をクリックして、認証コードのフォームに入力してください。






<img width="647" height="603" alt="スクリーンショット 2026-06-10 21 14 33" src="https://github.com/user-attachments/assets/27fff5ec-b146-4e79-b3c8-842c6234abf1" />









5.一般社員:一般社員のログイン画面が表示されます。



<img width="1056" height="603" alt="スクリーンショット 2026-06-10 21 15 07" src="https://github.com/user-attachments/assets/e689613b-cf0e-4f95-8c1e-ff19ef4141c2" />





6.勤怠登録の「出勤」と「退勤」では、手動での入力もしくは、時計のアイコンをクリックして、数字を選択しての時間設定を行い、出勤すると退勤するをクリックしてください。。※「出勤」のみが、出勤もしくは、リモートを選択することができます。






(出勤もしくは、リモートの場合)

<img width="478" height="371" alt="スクリーンショット 2026-06-10 21 43 57" src="https://github.com/user-attachments/assets/82780569-82eb-47ab-8b39-353fba04d1b2" />





(退勤の場合)




<img width="478" height="371" alt="スクリーンショット 2026-06-10 21 47 55" src="https://github.com/user-attachments/assets/d1988fc3-87a1-4e48-aa42-d985ce43c838" />




7.「勤怠の時間」の結果が表示されます。※もし、出勤もしくは、退勤で、間違って入力した時間を修正することも可能です。




<img width="478" height="467" alt="スクリーンショット 2026-06-10 21 49 56" src="https://github.com/user-attachments/assets/c65d8040-9c38-428c-88dc-9d205017084c" />






8.一般社員:休暇申請の場合、「休暇申請」をクリックします。→新規作成をクリックします。→「休暇種別」、「日時」、「申請理由」を入力して、「申請する」をクリックしてください。



<img width="522" height="139" alt="スクリーンショット 2026-06-14 20 20 31" src="https://github.com/user-attachments/assets/22b21822-0ceb-4d53-a8ad-9a2213c0b7de" />








<img width="896" height="457" alt="スクリーンショット 2026-06-14 20 21 17" src="https://github.com/user-attachments/assets/75f6eaf4-ea27-41dc-af29-ecfc17b6d7f4" />






<img width="896" height="575" alt="スクリーンショット 2026-06-14 20 22 46" src="https://github.com/user-attachments/assets/0751c42f-a9ae-41ab-9a27-7e76e4eb4bc8" />





※休暇申請で、日数が０の場合、申請できず、エラーになりますので、ご注意ください。



<img width="896" height="563" alt="スクリーンショット 2026-06-14 20 25 41" src="https://github.com/user-attachments/assets/b2c091c7-24c7-4f1e-a228-336770bad40c" /><img width="522" height="139" alt="スクリーンショット 2026-06-14 20 20 31" src="https://github.com/user-attachments/assets/31b16f5d-4e1e-46a0-b5e6-24e2981f961c" />











9.システム管理者:もし、休暇申請日数が足りない場合は、システム管理者で、メニューの中から「有給残日数管理」をクリックしてください。→「有給残日数管理」が表示されますので、一般ユーザーの中から編集をクリックしてください→休暇日数の数字を入力した上で、保存してください。









<img width="896" height="107" alt="スクリーンショット 2026-06-14 21 14 12" src="https://github.com/user-attachments/assets/627b006c-ea8e-4ca5-9bf6-24dcc20322bd" />













<img width="965" height="583" alt="スクリーンショット 2026-06-14 21 15 43" src="https://github.com/user-attachments/assets/4103c3ed-b5ae-4166-a12a-749b7e3f4fe6" />












<img width="965" height="66" alt="スクリーンショット 2026-06-14 21 17 37" src="https://github.com/user-attachments/assets/c2a3e30e-a9e4-43f6-95ad-8c85d6943369" />






10.承認担当者:通知が届きますので、通知を確認した上で、承認メニューの中から「休暇承認」をクリックしてください。→「承認」もしくは、「却下」を選択してください。コメントで、承認や却下の理由を添えると一般ユーザーも納得しますので、コメントを添えてから、「承認する」をクリックしてください。





<img width="965" height="158" alt="スクリーンショット 2026-06-14 21 21 49" src="https://github.com/user-attachments/assets/a3a54376-fc99-49e7-a8e4-14a6b4dd51c9" />







<img width="510" height="381" alt="スクリーンショット 2026-06-14 21 26 22" src="https://github.com/user-attachments/assets/bf3115ca-8655-40bd-ab92-cecc7674aa1b" />





11.一般社員：休暇申請で、「承認済み」になっていれば、休暇申請は受理されることになります。





<img width="948" height="342" alt="スクリーンショット 2026-06-14 21 27 05" src="https://github.com/user-attachments/assets/5ce97382-08e7-46ab-8d50-ac80fdd0003e" />







12:一般社員:残業時間を取る場合は、「残業申請」の所をクリックしてください。→「新規作成」をクリックしてください。






<img width="485" height="118" alt="スクリーンショット 2026-06-17 20 00 45" src="https://github.com/user-attachments/assets/08782ec6-2bdc-4eab-a9e9-9c3b08621ceb" />









<img width="847" height="118" alt="スクリーンショット 2026-06-17 20 06 18" src="https://github.com/user-attachments/assets/92ad0a16-e846-473f-93a0-ea7f44db57de" />









13.一般社員:残業日、時刻、申請理由を記入した上で、「申請する」をクリックしてください。







<img width="847" height="423" alt="スクリーンショット 2026-06-17 20 06 51" src="https://github.com/user-attachments/assets/12c6c529-41ac-4494-a2cb-65a6d244c34a" />







14:承認担当者:通知音が鳴り、「残業申請の通知」を確認します。







<img width="847" height="156" alt="スクリーンショット 2026-06-17 20 13 50" src="https://github.com/user-attachments/assets/06a71793-621e-4aa8-bba4-aef2c3a86909" />










15:承認担当者:承認メニューの中から「残業承認」をクリックします。→内容を確認した上で、「承認」もしくは、「却下」を選択してクリックした後、コメントを記入した上で、「承認する」もしくは、「却下する」を選択してクリックしてください。







<img width="1039" height="250" alt="スクリーンショット 2026-06-17 20 17 17" src="https://github.com/user-attachments/assets/cb9c1d0e-adc5-4088-9e85-d6075b885a0f" />







<img width="847" height="156" alt="スクリーンショット 2026-06-17 20 16 02" src="https://github.com/user-attachments/assets/7bedd040-f275-436d-ba85-0bbb3ca79f15" />






<img width="515" height="403" alt="スクリーンショット 2026-06-17 20 18 39" src="https://github.com/user-attachments/assets/8fef71e2-3854-4372-aadb-3b4d8fe948f9" />





16:承認担当者:「勤怠レポート」をクリックしてください。→勤怠、休暇、残業についてのデータをCSVでダウンロードしたり、印刷することができます。
※一般社員では、「勤怠レポート」を確認できない点は、気を付けてください。それとSafariでは、「印刷」を直接使用できないとなっていますので、ご注意ください。→ショートカットキーを使用すれば、印刷できます。Windows:Ctrl + P   Mac:command + P




<img width="616" height="108" alt="スクリーンショット 2026-06-14 21 48 15" src="https://github.com/user-attachments/assets/0e5d955c-a5ea-4e73-84a5-1016aa8c09ba" />







<img width="1146" height="539" alt="スクリーンショット 2026-06-14 21 50 07" src="https://github.com/user-attachments/assets/f8038e8a-639c-4b17-8e51-5f99d30129cf" />






※印刷成功した時の勤怠レポート(写真)





<img width="1280" height="832" alt="スクリーンショット 2026-06-17 21 30 31のコピー" src="https://github.com/user-attachments/assets/f0878127-8700-4295-9126-a6a6b36d57c4" />






17:一般社員：「プロフィール設定」をクリックしてください。→基本情報で、「社員ID」や「ロール」以外は、変更できます。





<img width="622" height="526" alt="スクリーンショット 2026-06-14 22 07 37" src="https://github.com/user-attachments/assets/72d7bcf6-2a54-4008-8585-cf7f8cdf3edc" />









18:システム管理者：管理者メニューの中で、「ユーザー管理」をクリックしてください。→新規一般社員のユーザーのアカウントを作ることができます。



<img width="622" height="104" alt="スクリーンショット 2026-06-14 22 09 20" src="https://github.com/user-attachments/assets/9e5f6ce6-9f7f-4554-a9ab-8265f267b481" />








<img width="622" height="542" alt="スクリーンショット 2026-06-14 22 11 13" src="https://github.com/user-attachments/assets/dcfbb06f-ff25-4e9e-a873-eb8d0ba171a7" />


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
