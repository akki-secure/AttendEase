"""api_client.pyのログイン・トークンキャッシュ・打刻ロジックのテスト(実サーバー不要)。"""

import importlib
import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def api_client_module(tmp_path, monkeypatch):
    monkeypatch.setenv("ATTENDEASE_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("ATTENDEASE_EMPLOYEE_ID", "EMP001")
    monkeypatch.setenv("ATTENDEASE_PASSWORD", "dummy-password")

    sys.modules.pop("api_client", None)
    import api_client as module

    importlib.reload(module)
    module.TOKEN_CACHE_PATH = tmp_path / "token_cache.json"
    return module


def mock_response(status_code: int, payload: dict) -> MagicMock:
    res = MagicMock()
    res.status_code = status_code
    res.json.return_value = payload
    if status_code >= 400:
        res.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    else:
        res.raise_for_status.side_effect = None
    return res


def test_login_prompts_otp_and_caches_token(api_client_module, monkeypatch):
    client = api_client_module.AttendEaseClient()
    assert client._token is None

    with patch("api_client.requests.post") as mock_post, patch("builtins.input", return_value="123456"):
        mock_post.side_effect = [
            mock_response(200, {"ok": True, "email_hint": "t***@example.com"}),
            mock_response(200, {"access_token": "jwt-token-abc"}),
        ]
        client.login()

    assert client._token == "jwt-token-abc"
    cache = json.loads(api_client_module.TOKEN_CACHE_PATH.read_text())
    assert cache["access_token"] == "jwt-token-abc"
    assert cache["employee_id"] == "EMP001"


def test_cached_token_is_reused_without_login(api_client_module):
    api_client_module.TOKEN_CACHE_PATH.write_text(
        json.dumps({"employee_id": "EMP001", "access_token": "cached-token", "obtained_at": time.time()})
    )

    client = api_client_module.AttendEaseClient()
    assert client._token == "cached-token"

    with patch("api_client.requests.post") as mock_post:
        client.ensure_logged_in()
        mock_post.assert_not_called()  # キャッシュが有効ならログインAPIを呼ばない


def test_expired_cached_token_triggers_relogin(api_client_module):
    stale_time = time.time() - (api_client_module.TOKEN_MAX_AGE_SECONDS + 60)
    api_client_module.TOKEN_CACHE_PATH.write_text(
        json.dumps({"employee_id": "EMP001", "access_token": "old-token", "obtained_at": stale_time})
    )

    client = api_client_module.AttendEaseClient()
    assert client._token is None  # 期限切れなのでキャッシュは使われない


def test_request_retries_once_on_401(api_client_module):
    client = api_client_module.AttendEaseClient()
    client._token = "expired-token"

    with patch("api_client.requests.request") as mock_request, patch.object(
        client, "login", side_effect=lambda: setattr(client, "_token", "new-token")
    ) as mock_login:
        mock_request.side_effect = [
            mock_response(401, {}),
            mock_response(200, {"status": "NOT_CLOCKED_IN", "date": "2026-08-01", "record": None}),
        ]
        result = client.get_today_status()

    mock_login.assert_called_once()
    assert result["status"] == "NOT_CLOCKED_IN"
    assert mock_request.call_count == 2


def test_clock_in_sends_work_type(api_client_module):
    client = api_client_module.AttendEaseClient()
    client._token = "valid-token"

    with patch("api_client.requests.request") as mock_request:
        mock_request.return_value = mock_response(201, {"id": 1, "work_type": "remote"})
        client.clock_in("remote")

    _, kwargs = mock_request.call_args
    assert kwargs["json"] == {"work_type": "remote"}
