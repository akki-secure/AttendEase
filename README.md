# AttendEase - 勤怠管理システム

小規模チーム（〜50人）向けの勤怠登録・管理アプリです。無料のOSS技術のみで構築しています。

## 目的


業務アプリを設計・実装できるレベルにあることを示すために、「勤怠管理システム」を題材に選びました。

---

> [!IMPORTANT]
> **複数ユーザーで同時に動作確認する場合は、異なるブラウザを使用してください。**
> 同一ブラウザでは複数タブを開いてもセッションが共有されるため、別ユーザーとしてログインできません。
> （例：管理者はBrave 、一般社員は Google Chrome、承認担当者は Safariの中のGoogleChrome）


> [!WARNING]
> **AWSでデプロイ状態の場合の注意点**
>
> デプロイ先URL: https://attendease2026.duckdns.org/login
>
> 低い性能のAWSの「t3.micro」サーバーを使って、イベント処理が遅れているため、ログイン時や登録などにエラーが起きますが、２回~3回試さないと成功できませんので、ご注意ください。
> データ取得失敗などでデータが表示されない場合は、「再読み込み（リロード）」してください。

> [!WARNING]
> **ジオフェンス機能（現在地取得）がmacOSで失敗する場合**
>
> ブラウザ・OS双方で位置情報の利用を許可しているにもかかわらず「現在地の取得に失敗しました」となる場合、macOSの位置情報デーモン（`locationd`）が内部的にスタックしていることがあります。
> ターミナルで以下を実行し、デーモンを再起動してから再度お試しください（sudoパスワードの入力が必要です）。
> ```bash
> sudo killall locationd
> ```

---
## AttendEase(勤怠管理システム)の流れ
1.「http://localhost:3000/login」（ローカルでDocker起動している場合）、またはAWSにデプロイしている場合は上記「デプロイ先URL」にアクセスすると「社員ログイン」の画面が、表示されます。


<img width="647" height="567" alt="スクリーンショット 2026-06-10 20 53 01" src="https://github.com/user-attachments/assets/62bdd3c4-bfa1-4c42-a57a-6fb16f05c159" />


2.一般社員:新規ログインする場合は、新規登録をクリックしてください。新規登録の完了を登録をする前に、必ず、「社員ID」と「パスワード」はメモするようにお願いします。新規アカウントに必要な「社員ID」、「氏名」、「メールアドレス」、「パスワード」を入力して、「登録」をクリックして完了するとログイン画面に戻り、新規アカウントの作成が完了しました。


<img width="647" height="603" alt="スクリーンショット 2026-06-10 20 56 01" src="https://github.com/user-attachments/assets/28d5007c-bba1-4bdc-8210-59e8f93899bc" />


⚠️既存のアカウントで、正しいユーザーIDとパスワードを入力に「３回失敗」すると「アカウントロックになりますので、ご注意ください。


<img width="486" height="604" alt="スクリーンショット 2026-06-14 18 33 49" src="https://github.com/user-attachments/assets/40fe3091-e631-4a83-8667-e8a75e3b76c1" />


3.一般社員:新規アカウントで作成したユーザーIDとパスワードを入力後、「次へ進む」をクリックしてください。


<img width="647" height="603" alt="スクリーンショット 2026-06-10 21 10 50" src="https://github.com/user-attachments/assets/bd626dd7-8b58-45f3-a70a-21fe0e562f80" />


※間違った社員IDまたはパスワードを入力してログインしますと、「社員IDまたはパスワードが正しくありません」とエラーが表示されますので、ご注意ください。


<img width="647" height="603" alt="スクリーンショット 2026-06-10 21 08 40" src="https://github.com/user-attachments/assets/f35ce9e7-1a7d-481d-89b4-d4d7cb8b16a9" />


4.一般社員:「認証コード」を認証コードのフォームに入力して、ログインしてください。※もし、時間内に入力できない場合は、「再送信」をクリックして、認証コードのフォームに入力してください。


<img width="647" height="603" alt="スクリーンショット 2026-06-10 21 14 33" src="https://github.com/user-attachments/assets/27fff5ec-b146-4e79-b3c8-842c6234abf1" />


5.一般社員:一般社員のログイン画面が表示されます。


<img width="1056" height="603" alt="スクリーンショット 2026-06-10 21 15 07" src="https://github.com/user-attachments/assets/e689613b-cf0e-4f95-8c1e-ff19ef4141c2" />


6.勤怠登録の「出勤」と「退勤」では、手動での入力もしくは、時計のアイコンをクリックして、数字を選択しての時間設定を行い、出勤すると退勤するをクリックしてください。※「出勤」のみが、出勤もしくは、リモートを選択することができます。


(出勤もしくは、リモートの場合)

<img width="478" height="371" alt="スクリーンショット 2026-06-10 21 43 57" src="https://github.com/user-attachments/assets/82780569-82eb-47ab-8b39-353fba04d1b2" />


(退勤の場合)


<img width="478" height="371" alt="スクリーンショット 2026-06-10 21 47 55" src="https://github.com/user-attachments/assets/d1988fc3-87a1-4e48-aa42-d985ce43c838" />


7.「勤怠の時間」の結果が表示されます。※もし、出勤もしくは、退勤で、間違って入力した時間を修正することも可能です。


<img width="478" height="467" alt="スクリーンショット 2026-06-10 21 49 56" src="https://github.com/user-attachments/assets/c65d8040-9c38-428c-88dc-9d205017084c" />


8.一般社員:休暇申請の場合、「休暇申請」をクリックします。→新規作成をクリックします。→「休暇種別」、「日時」、「申請理由」を入力して、「申請する」をクリックしてください。

※休暇種別で「特別休暇」を選択した場合は、通常の「申請理由」欄の代わりに「特別休暇の種類」（慶弔休暇（弔事・慶事）／出産休暇／創立記念日休暇／その他）を選択式で選ぶ必要があります。未選択のままだと「特別休暇の種類を選択してください」というエラーになり、申請できません。「補足（任意）」欄に自由記述で詳細を追記することもできます。


<img width="522" height="139" alt="スクリーンショット 2026-06-14 20 20 31" src="https://github.com/user-attachments/assets/22b21822-0ceb-4d53-a8ad-9a2213c0b7de" />


<img width="896" height="457" alt="スクリーンショット 2026-06-14 20 21 17" src="https://github.com/user-attachments/assets/75f6eaf4-ea27-41dc-af29-ecfc17b6d7f4" />


<img width="896" height="575" alt="スクリーンショット 2026-06-14 20 22 46" src="https://github.com/user-attachments/assets/0751c42f-a9ae-41ab-9a27-7e76e4eb4bc8" />


※休暇申請で、日数が０の場合、申請できず、エラーになりますので、ご注意ください。


<img width="896" height="563" alt="スクリーンショット 2026-06-14 20 25 41" src="https://github.com/user-attachments/assets/b2c091c7-24c7-4f1e-a228-336770bad40c" />

<img width="522" height="139" alt="スクリーンショット 2026-06-14 20 20 31" src="https://github.com/user-attachments/assets/31b16f5d-4e1e-46a0-b5e6-24e2981f961c" />


9.システム管理者:もし、休暇申請日数が足りない場合は、システム管理者で、メニューの中から「有給残日数管理」をクリックしてください。→「有給残日数管理」が表示されますので、一般ユーザーの中から編集をクリックしてください→休暇日数の数字を入力した上で、保存してください。


<img width="896" height="107" alt="スクリーンショット 2026-06-14 21 14 12" src="https://github.com/user-attachments/assets/627b006c-ea8e-4ca5-9bf6-24dcc20322bd" />


<img width="965" height="583" alt="スクリーンショット 2026-06-14 21 15 43" src="https://github.com/user-attachments/assets/4103c3ed-b5ae-4166-a12a-749b7e3f4fe6" />


<img width="965" height="66" alt="スクリーンショット 2026-06-14 21 17 37" src="https://github.com/user-attachments/assets/c2a3e30e-a9e4-43f6-95ad-8c85d6943369" />


10.承認担当者:通知が届きますので、通知を確認した上で、承認メニューの中から「休暇承認」をクリックしてください。→「承認」もしくは、「却下」を選択してください。コメントで、承認や却下の理由を添えると一般ユーザーも納得しますので、コメントを添えてから、「承認する」をクリックしてください。


<img width="965" height="158" alt="スクリーンショット 2026-06-14 21 21 49" src="https://github.com/user-attachments/assets/a3a54376-fc99-49e7-a8e4-14a6b4dd51c9" />


<img width="510" height="381" alt="スクリーンショット 2026-06-14 21 26 22" src="https://github.com/user-attachments/assets/bf3115ca-8655-40bd-ab92-cecc7674aa1b" />


11.一般社員：休暇申請で、「承認済み」になっていれば、休暇申請は受理されることになります。


<img width="948" height="342" alt="スクリーンショット 2026-06-14 21 27 05" src="https://github.com/user-attachments/assets/5ce97382-08e7-46ab-8d50-ac80fdd0003e" />


12.一般社員:残業時間を取る場合は、「残業申請」の所をクリックしてください。→「新規作成」をクリックしてください。


<img width="485" height="118" alt="スクリーンショット 2026-06-17 20 00 45" src="https://github.com/user-attachments/assets/08782ec6-2bdc-4eab-a9e9-9c3b08621ceb" />


<img width="847" height="118" alt="スクリーンショット 2026-06-17 20 06 18" src="https://github.com/user-attachments/assets/92ad0a16-e846-473f-93a0-ea7f44db57de" />


13.一般社員:残業日、時刻、申請理由を記入した上で、「申請する」をクリックしてください。


<img width="847" height="423" alt="スクリーンショット 2026-06-17 20 06 51" src="https://github.com/user-attachments/assets/12c6c529-41ac-4494-a2cb-65a6d244c34a" />


14.承認担当者:通知音が鳴り、「残業申請の通知」を確認します。


<img width="847" height="156" alt="スクリーンショット 2026-06-17 20 13 50" src="https://github.com/user-attachments/assets/06a71793-621e-4aa8-bba4-aef2c3a86909" />


15.承認担当者:承認メニューの中から「残業承認」をクリックします。→内容を確認した上で、「承認」もしくは、「却下」を選択してクリックした後、コメントを記入した上で、「承認する」もしくは、「却下する」を選択してクリックしてください。


<img width="1039" height="250" alt="スクリーンショット 2026-06-17 20 17 17" src="https://github.com/user-attachments/assets/cb9c1d0e-adc5-4088-9e85-d6075b885a0f" />


<img width="847" height="156" alt="スクリーンショット 2026-06-17 20 16 02" src="https://github.com/user-attachments/assets/7bedd040-f275-436d-ba85-0bbb3ca79f15" />


<img width="515" height="403" alt="スクリーンショット 2026-06-17 20 18 39" src="https://github.com/user-attachments/assets/8fef71e2-3854-4372-aadb-3b4d8fe948f9" />


16.承認担当者:「勤怠レポート」をクリックしてください。→勤怠、休暇、残業についてのデータをCSVでダウンロードしたり、印刷することができます。
※一般社員では、「勤怠レポート」を確認できない点は、気を付けてください。それとSafariでは、「印刷」を直接使用できないとなっていますので、ご注意ください。→ショートカットキーを使用すれば、印刷できます。Windows:Ctrl + P   Mac:command + P


<img width="616" height="108" alt="スクリーンショット 2026-06-14 21 48 15" src="https://github.com/user-attachments/assets/0e5d955c-a5ea-4e73-84a5-1016aa8c09ba" />


<img width="1146" height="539" alt="スクリーンショット 2026-06-14 21 50 07" src="https://github.com/user-attachments/assets/f8038e8a-639c-4b17-8e51-5f99d30129cf" />


※印刷成功した時の勤怠レポート(写真)


<img width="1280" height="832" alt="スクリーンショット 2026-06-17 21 30 31のコピー" src="https://github.com/user-attachments/assets/f0878127-8700-4295-9126-a6a6b36d57c4" />


17.一般社員：「プロフィール設定」をクリックしてください。→基本情報で、「社員ID」や「ロール」以外は、変更できます。


<img width="622" height="526" alt="スクリーンショット 2026-06-14 22 07 37" src="https://github.com/user-attachments/assets/72d7bcf6-2a54-4008-8585-cf7f8cdf3edc" />


18.システム管理者：管理者メニューの中で、「ユーザー管理」をクリックしてください。→新規一般社員のユーザーのアカウントを作ることができます。


<img width="1277" height="183" alt="スクリーンショット 2026-07-18 11 40 20" src="https://github.com/user-attachments/assets/93a2f15d-47c7-403a-a239-9562f625fd1b" />


<img width="622" height="542" alt="スクリーンショット 2026-06-14 22 11 13" src="https://github.com/user-attachments/assets/dcfbb06f-ff25-4e9e-a873-eb8d0ba171a7" />


19.システム管理者:管理者メニューの中で、「拠点・ジオフェンス管理」をクリックしてください。


20.システム管理者:「拠点を追加」をクリックしてください。→「拠点名」、「緯度」、「経度」、「許容半径(メートル)」、「有効にする」を入力してください。※「↖️現在地」を使用することで、緯度と経度は、自動入力することができます。(位置情報を許可する必要があるので、「サイトへのアクセス時は、許可」もしくは、「今回のみ許可」どちらかをクリックしてください。)→「保存」をクリックしてください。


<img width="1277" height="183" alt="スクリーンショット 2026-07-18 11 34 22" src="https://github.com/user-attachments/assets/901832a7-84eb-4314-911a-e09b75b4a103" />


<img width="316" height="295" alt="スクリーンショット 2026-07-18 12 53 47" src="https://github.com/user-attachments/assets/2e401ab4-7ee0-4ac5-bf41-8ca2ca04205b" />


<img width="517" height="477" alt="スクリーンショット 2026-07-18 12 52 58" src="https://github.com/user-attachments/assets/19f6b4fe-ef31-4e73-9982-c3987e0b4d88" />


<img width="590" height="162" alt="スクリーンショット 2026-07-19 5 38 48" src="https://github.com/user-attachments/assets/1b2d283a-0780-4b03-b04f-67a338bc3e03" />


21.一般社員：システム管理者が、ジオフェンス機能を「ON」にしている場合のみ、GPSをONにして、なりすましの出勤と退勤を防ぐために、ジオフェンス機能で定めた範囲外での出勤もしくは、退勤での時間の入力ができない、修正もできない、勤怠一覧での前日の出勤と退勤での登録も出来ないようになっています。
※ジオフェンス機能をOFFにすることで、出勤もしくは、退勤での時間のジオフェンスで定めた範囲外での手動入力、修正、勤怠一覧での前日の出勤と退勤での登録もできるようになります。


<img width="1149" height="534" alt="スクリーンショット 2026-07-19 8 55 58" src="https://github.com/user-attachments/assets/a2bd1014-ec50-4416-802f-5ed409ff73fd" />


<img width="515" height="520" alt="スクリーンショット 2026-07-19 8 53 40" src="https://github.com/user-attachments/assets/116926a3-310d-4577-bdd7-d7f3ba1496ad" />


22.一般社員:ジオフェンス機能ONでの場合、勤怠一覧で、「状態」は「ジオフェンス」として確認することができます。


<img width="1277" height="183" alt="スクリーンショット 2026-07-18 11 44 30" src="https://github.com/user-attachments/assets/02f4ffab-f957-416f-b257-36fb1a577bdc" />


23.システム管理者：一般社員などのユーザーが社員ログインで、「アカウントロック」→「ユーザー一覧」をクリックして、「ロック」と表記されたユーザーを探して、項目の「操作」にある「ロック解除」をクリックすると、アカウントロックが解除されます。


<img width="918" height="479" alt="スクリーンショット 2026-07-19 9 43 04" src="https://github.com/user-attachments/assets/a4d9f38e-3fb9-4145-a001-f7f554792750" />


<img width="918" height="479" alt="スクリーンショット 2026-07-19 9 43 17" src="https://github.com/user-attachments/assets/74145c32-8eb0-4a53-bfce-c7fa49683ea7" />


24.システム管理者:ユーザー一覧の操作項目の「履歴」で確認でき、アカウントロックの解除の時だけ操作の不正防止を防ぐ為に、監査ログとして「いつ、誰が、何を」 というログを残せるようにしています。


<img width="918" height="62" alt="スクリーンショット 2026-07-19 13 09 18" src="https://github.com/user-attachments/assets/0d57b943-24ac-4389-82c4-ab83d64faef7" />


<img width="515" height="233" alt="スクリーンショット 2026-07-19 13 09 41" src="https://github.com/user-attachments/assets/e71ba0af-4350-48b8-ac04-835935f00a86" />


---

## 機能

- 出退勤打刻（修正申請あり）
- ジオフェンス打刻制限（登録拠点の半径内でのみ打刻を許可、ADMINが拠点・ON/OFFを管理。位置情報取得はHTTPS環境が必須）
- アカウントロック解除・監査ログ（ログイン失敗が続くとロックされたアカウントをADMINが解除可能。「いつ・誰が」解除したかの履歴を記録）
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
| インフラ | Docker / Docker Compose / AWS EC2 (t3.micro) / nginx / Let's Encrypt (Certbot) / DuckDNS |
| CI/CD | GitHub Actions |

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

> [!NOTE]
> DBマイグレーション(`alembic upgrade head`)はbackendコンテナ起動時に自動実行されます。手動で実行する必要はありません。

**4. テストユーザーの投入**

```bash
docker compose exec backend python -m scripts.seed
```

**5. （IDEで型補完・型チェックを効かせる場合）frontendの依存関係をホスト側にもインストール**

`frontend/node_modules` と `frontend/.nuxt` は `docker-compose.yml` でコンテナ内の匿名ボリュームとして扱われるため、`npm install` をコンテナ内で実行してもホスト側（VSCode等のIDEが参照する場所）には反映されません。IDEで `process is not defined` 等の型エラーが表示される場合は、以下をホスト側で実行してください。

```bash
cd frontend
npm install
```

依存関係やNuxtのバージョンを更新した際は、このコマンドをホスト側でも再実行する必要があります。

**6. ブラウザでアクセス**

| URL | 説明 |
|-----|------|
| http://localhost:3000 | フロントエンド |
| http://localhost:8000/docs | バックエンド API ドキュメント |

### テストユーザー

| 社員ID | パスワード | ロール | 氏名 |
|--------|-----------|--------|------|
| ADMIN001 | Admin1234! | システム管理者 | システム管理者 |
| EMP002 | NewPass456! | 承認担当者 | 鈴木花子 |
| EMP001 | Password1! | 一般社員 | 山田太郎 |

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

## 本番環境（HTTPS化）

ジオフェンス機能はブラウザの Geolocation API を使用しており、セキュアコンテキスト（HTTPS、または `localhost`）でしか動作しない。そのため本番環境（AWS EC2）は以下の構成でHTTPS化している。

- **DuckDNS**: 無料のダイナミックDNSでサブドメイン（例: `attendease2026.duckdns.org`）を取得し、EC2のパブリックIPに割り当て
- **Elastic IP**: EC2再起動時にIPアドレスが変わらないよう固定IPを割り当て済み
- **nginx**: リバースプロキシとして `/api/` 配下はbackend、それ以外はfrontendへ振り分け（`nginx/templates/default.conf.template`）。frontend/backendのポート（3000/8000）は外部に直接公開していない
- **Let's Encrypt（Certbot）**: 無料のTLS証明書を取得・自動更新（`docker-compose.prod.yml` の `certbot` サービスが12時間ごとに更新を試行、有効期限90日）
- 初回証明書発行は `scripts/init-letsencrypt.sh` を使用（`DOMAIN=xxx.duckdns.org ./scripts/init-letsencrypt.sh`）

`NUXT_PUBLIC_API_BASE` は同一オリジン構成のため空文字（相対パス）で運用し、CORSも同一オリジンで完結する。

---

## CI/CD

GitHub Actions で CI（テスト）と CD（本番デプロイ）を自動化している。

### CI（`.github/workflows/ci.yml`）

`main` への push・PR時に以下を並行実行する。

| ジョブ | 内容 |
|--------|------|
| backend-test | Python 3.12 で依存関係をインストールし `pytest` を実行 |
| frontend-build | Node.js 22 で `npm ci` → ESLint → `npm run build` |

### CD（`.github/workflows/deploy.yml`）

`main` への push をトリガーに、EC2への自動デプロイを行う。

1. GitHub ActionsランナーのグローバルIPを取得
2. AWSセキュリティグループのSSHポート(22番)に、そのIPのみを一時的に許可
3. SSHでEC2に接続し、最新の `main` を pull → 不要なDockerイメージ・ビルドキャッシュを削除 → `docker-compose.prod.yml` でコンテナを再ビルド・再起動
4. デプロイ完了後（成功・失敗を問わず）、一時許可したSSHアクセスを取り消す

> [!NOTE]
> SSHの22番ポートは常時開放せず、デプロイの実行中のみGitHub ActionsのIPを許可する方式にすることで、待ち受け範囲を最小限にしている。

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
    AdminUsers("👥 ユーザー管理\n/admin/users\n（アカウントロック解除・監査ログ）")
    AdminLeave("📋 有給残日数管理\n/admin/leave-balances")
    AdminLocations("📍 拠点・ジオフェンス管理\n/admin/locations")
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
  Dashboard -->|"ADMIN"| AdminLocations

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
    int failed_login_count "3以上でロック。管理者が解除可能"
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
    bool clock_in_geofence_verified
    bool clock_out_geofence_verified
    text correction_note
    datetime original_clock_in
    datetime original_clock_out
    int original_break_minutes
    string original_status
    int reviewer_id FK
    text reviewer_comment
    datetime reviewed_at
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
    time scheduled_time
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

  office_locations {
    int id PK
    string name
    float latitude
    float longitude
    int radius_meters
    bool is_active
    datetime created_at
    datetime updated_at
  }

  geofence_settings {
    int id PK
    bool enabled
    datetime updated_at
  }

  account_unlock_logs {
    int id PK
    int user_id FK
    int unlocked_by_id FK
    datetime created_at
  }

  users ||--o{ attendance_records : "打刻"
  users ||--o{ leave_requests : "申請"
  users ||--o{ overtime_requests : "申請"
  users ||--o{ leave_balances : "残日数"
  users ||--o{ notifications : "通知"
  users ||--o{ leave_requests : "承認"
  users ||--o{ overtime_requests : "承認"
  users ||--o{ attendance_records : "打刻修正承認"
  users ||--o{ account_unlock_logs : "ロック解除対象"
  users ||--o{ account_unlock_logs : "ロック解除実行者"
```

---

## ブランチ運用ルール

- `main` ブランチへの直接 push は禁止しています
- 作業は `feature/xxx` などのブランチで行い、Pull Request を通してください

```bash
git checkout -b feature/your-branch-name
```

---

## おまけ機能: CoDroneEDUコントローラーでの打刻連携

RoboLink社の「CoDroneEDU」というドローン教育キットのコントローラーを使って、ボタン操作でAttendEaseに出勤・退勤を打刻できる概念実証です。ポートフォリオとしての技術アピール・遊び心を目的としたもので、AttendEase本体（`backend/`, `frontend/`）のコードは一切変更しておらず、`integrations/codrone/`配下の独立したPythonスクリプトとして動作します。

### 操作フロー図

```mermaid
flowchart TD
  Start(["🚀 python bridge.py 起動"]) --> Otp["📧 認証コード(OTP)入力\n(初回のみ)"]
  Otp --> Pair["🔌 コントローラーとペアリング"]
  Pair --> Ready["✅ 接続完了・待機中"]

  Ready -->|"十字ボタン ← "| Office["🏢 出社モード\n(LED青)"]
  Ready -->|"十字ボタン → "| Remote["🏠 リモートモード\n(LED緑)"]
  Office --> Ready
  Remote --> Ready

  Ready -->|"Sボタン1.5秒長押し"| Toggle{"現在の状態は？"}
  Toggle -->|"未出勤"| ClockIn["🎵 出勤を記録\n(上昇メロディ)"]
  Toggle -->|"出勤中"| ClockOut["🎵 退勤を記録\n(下降メロディ)"]
  Toggle -->|"本日完了済み"| Done["💬 案内メッセージのみ\n(エラーにはならない)"]
  Toggle -->|"通信エラー等"| Error["🔴 赤LED点滅+エラー音"]

  ClockIn --> Ready
  ClockOut --> Ready
  Done --> Ready
  Error --> Ready
```

### Windowsでのセットアップ手順

AttendEase本体は既にAWS EC2（`https://attendease2026.duckdns.org`）にデプロイ済みのため、Docker等のセットアップは不要です。コントローラー用のフォルダだけを取得して動かします。

1. **Gitをインストール**（未導入の場合）: [git-scm.com](https://git-scm.com/downloads) からダウンロードし、デフォルト設定のままインストール
2. **リポジトリを取得**
   ```
   git clone https://github.com/akki-secure/AttendEase.git
   cd AttendEase\integrations\codrone
   ```
3. **Pythonをインストール**（未導入の場合）: [python.org](https://www.python.org/downloads/) から**3.12系**をダウンロード（3.14など最新すぎるバージョンは一部パッケージのビルドに失敗する事例あり）。インストール時は「**Add python.exe to PATH**」に必ずチェック
4. **依存パッケージをインストール**
   ```
   pip install -r requirements.txt
   ```
5. **`.env`ファイルを作成**
   ```
   copy .env.example .env
   notepad .env
   ```
   以下を設定:
   ```
   ATTENDEASE_BASE_URL=https://attendease2026.duckdns.org
   ATTENDEASE_EMPLOYEE_ID=(あなたの社員ID)
   ATTENDEASE_PASSWORD=(あなたのパスワード)
   CODRONE_PORT=(任意。自動ペアリングが失敗する場合にCOMポート番号を指定)
   ```
6. **USBケーブルでコントローラーを接続**し、電源ボタンを押して起動
7. **起動**
   ```
   python bridge.py
   ```
   コンソールの案内に従い、登録メールに届いた6桁の認証コード（OTP）を入力するとログインが完了し、コントローラーとのペアリングが始まります。「接続完了」と表示されたら操作可能です。

### 操作方法

| 操作 | ボタン | 内容 |
|---|---|---|
| 出社モードにする | 十字ボタン「左」 | LEDが青になる |
| リモートモードにする | 十字ボタン「右」 | LEDが緑になる |
| 出勤/退勤を打刻 | Sボタンを1.5秒以上長押し | 現在の状態を見て出勤/退勤を自動判定して記録 |

出勤成功時は上昇するメロディ、退勤成功時は下降するメロディが鳴ります。通信エラーなど打刻に失敗した場合は、LEDが赤く点滅し低い音のエラー音が鳴ります。

コントローラーでできるのは「現在時刻でのリアルタイムな出退勤打刻」と「出社/リモート切り替え」のみです。時刻を指定した登録・修正、休暇申請、月次確認などは引き続きブラウザから操作してください。

### トラブルシューティング

> [!WARNING]
> **`python`コマンドがMicrosoft Storeのダミーに反応してしまう場合**
>
> `python --version`でバージョンが表示されない、または`python bridge.py`を実行しても`bridge.py`が実行されずPython自体の情報だけが表示されて終わる場合、Windows標準の「アプリ実行エイリアス」が正規インストールしたPythonより優先されている可能性があります。
>
> `where python`を実行し、一番上が`...\WindowsApps\python.exe`になっていないか確認してください。該当する場合は以下のいずれかで対処できます。
> - 設定 → アプリ → 詳細なアプリ設定 → アプリ実行エイリアス で「python.exe」「python3.exe」をオフにする
> - `python`の代わりに`py`コマンドを使う（例: `py bridge.py`、`py -m pip install -r requirements.txt`）

> [!NOTE]
> **ペアリング時に`Could not connect to CoDrone EDU. Check that the drone is on and paired to the controller.`と表示される**
>
> これはCoDroneEDU SDKが物理的なドローン本体の飛行可能状態を確認しようとして失敗しているだけの警告で、処理を止めるものではありません。コントローラー単体でのUSB接続自体は成功しており、続けて「接続完了」と表示されればそのまま操作できます（実機確認済み）。

> [!NOTE]
> **本日すでに退勤済み（CLOSED状態）の場合**
>
> Sボタンを長押ししても「本日は既に処理済みのため打刻できません」と案内が表示されるだけで、エラーにはなりません。1日1往復（出勤→退勤）までの仕様のため、翌日改めてお試しください。
