"""AttendEase APIのラッパー(ログイン・トークンキャッシュ・打刻)。"""

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE_URL = os.environ["ATTENDEASE_BASE_URL"]
EMPLOYEE_ID = os.environ["ATTENDEASE_EMPLOYEE_ID"]
PASSWORD = os.environ["ATTENDEASE_PASSWORD"]

TOKEN_CACHE_PATH = Path(__file__).parent / "token_cache.json"
# サーバー側のトークン有効期限(8時間)より短めにみて、余裕を持って再ログインする
TOKEN_MAX_AGE_SECONDS = 7 * 60 * 60


class AttendEaseClient:
    def __init__(self) -> None:
        self._token: str | None = None
        self._load_cached_token()

    def _load_cached_token(self) -> None:
        if not TOKEN_CACHE_PATH.exists():
            return
        cache = json.loads(TOKEN_CACHE_PATH.read_text())
        age = time.time() - cache.get("obtained_at", 0)
        if cache.get("employee_id") == EMPLOYEE_ID and age < TOKEN_MAX_AGE_SECONDS:
            self._token = cache["access_token"]

    def _save_token(self, token: str) -> None:
        self._token = token
        TOKEN_CACHE_PATH.write_text(
            json.dumps({"employee_id": EMPLOYEE_ID, "access_token": token, "obtained_at": time.time()})
        )

    def login(self) -> None:
        pre_check_res = requests.post(
            f"{BASE_URL}/api/v1/auth/pre-check",
            json={"employee_id": EMPLOYEE_ID, "password": PASSWORD},
        )
        pre_check_res.raise_for_status()
        print(f"認証コードを送信しました: {pre_check_res.json().get('email_hint')}")

        otp = input("メールで届いた認証コード(6桁)を入力してください: ").strip()
        login_res = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"employee_id": EMPLOYEE_ID, "otp": otp},
        )
        login_res.raise_for_status()
        self._save_token(login_res.json()["access_token"])
        print("ログインに成功しました。")

    def ensure_logged_in(self) -> None:
        if self._token is None:
            self.login()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        self.ensure_logged_in()
        headers = {"Authorization": f"Bearer {self._token}"}
        res = requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)
        if res.status_code == 401:
            # トークン失効時は1回だけ再ログインしてリトライ
            self.login()
            headers = {"Authorization": f"Bearer {self._token}"}
            res = requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)
        res.raise_for_status()
        return res

    def get_today_status(self) -> dict:
        return self._request("GET", "/api/v1/attendance/today").json()

    def clock_in(self, work_type: str) -> dict:
        return self._request(
            "POST", "/api/v1/attendance/clock-in", json={"work_type": work_type}
        ).json()

    def clock_out(self) -> dict:
        return self._request("POST", "/api/v1/attendance/clock-out", json={}).json()
