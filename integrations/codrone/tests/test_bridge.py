"""bridge.pyの打刻判定ロジックのテスト(実機・実サーバー不要)。"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge import _handle_toggle_clock  # noqa: E402


def test_not_clocked_in_triggers_clock_in():
    client = MagicMock()
    client.get_today_status.return_value = {"status": "NOT_CLOCKED_IN"}
    drone = MagicMock()

    with patch("bridge.feedback") as mock_feedback:
        _handle_toggle_clock(client, drone, "office")

    client.clock_in.assert_called_once_with("office")
    client.clock_out.assert_not_called()
    mock_feedback.play_clock_in_sound.assert_called_once_with(drone)


def test_present_triggers_clock_out():
    client = MagicMock()
    client.get_today_status.return_value = {"status": "PRESENT"}
    drone = MagicMock()

    with patch("bridge.feedback") as mock_feedback:
        _handle_toggle_clock(client, drone, "office")

    client.clock_out.assert_called_once()
    client.clock_in.assert_not_called()
    mock_feedback.play_clock_out_sound.assert_called_once_with(drone)


def test_api_failure_triggers_error_feedback():
    client = MagicMock()
    client.get_today_status.side_effect = Exception("network error")
    drone = MagicMock()

    with patch("bridge.feedback") as mock_feedback:
        _handle_toggle_clock(client, drone, "office")

    mock_feedback.led_error.assert_called_once_with(drone)
    mock_feedback.play_error_sound.assert_called_once_with(drone)
