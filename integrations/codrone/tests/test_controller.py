"""controller.pyのボタンイベント検知ロジックのテスト(実機・実SDK不要)。"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from controller import LONG_PRESS_SECONDS, Controller  # noqa: E402


def make_controller() -> Controller:
    controller = Controller.__new__(Controller)
    controller.drone = MagicMock()
    controller.drone.s_pressed.return_value = False
    controller.drone.left_arrow_pressed.return_value = False
    controller.drone.right_arrow_pressed.return_value = False
    controller._toggle_pressed_since = None
    controller._toggle_long_press_fired = False
    controller._prev_left = False
    controller._prev_right = False
    return controller


def set_toggle(controller: Controller, pressed: bool) -> None:
    controller.drone.s_pressed.return_value = pressed


def set_arrows(controller: Controller, left: bool, right: bool) -> None:
    controller.drone.left_arrow_pressed.return_value = left
    controller.drone.right_arrow_pressed.return_value = right


def test_toggle_short_press_does_not_fire(monkeypatch):
    controller = make_controller()
    t = [0.0]
    monkeypatch.setattr("controller.time.monotonic", lambda: t[0])

    set_toggle(controller, True)
    assert controller.poll_events() is None  # 押した瞬間はまだ発火しない

    t[0] += LONG_PRESS_SECONDS - 0.1
    assert controller.poll_events() is None  # 長押し未満

    set_toggle(controller, False)
    assert controller.poll_events() is None  # 離したら発火しない


def test_toggle_long_press_fires_once(monkeypatch):
    controller = make_controller()
    t = [0.0]
    monkeypatch.setattr("controller.time.monotonic", lambda: t[0])

    set_toggle(controller, True)
    controller.poll_events()

    t[0] += LONG_PRESS_SECONDS + 0.1
    assert controller.poll_events() == "toggle_clock"
    assert controller.poll_events() is None  # 押しっぱなしでも連続発火しない

    set_toggle(controller, False)
    controller.poll_events()
    set_toggle(controller, True)
    controller.poll_events()  # 長押しタイマーの起点
    t[0] += LONG_PRESS_SECONDS + 0.1
    assert controller.poll_events() == "toggle_clock"  # 離して再度長押しすれば再発火


def test_mode_switch_edge_triggered(monkeypatch):
    controller = make_controller()
    monkeypatch.setattr("controller.time.monotonic", lambda: 0.0)
    set_toggle(controller, False)

    set_arrows(controller, left=True, right=False)
    assert controller.poll_events() == "mode_office"
    assert controller.poll_events() is None  # 押しっぱなしでは連続発火しない

    set_arrows(controller, left=False, right=True)
    assert controller.poll_events() == "mode_remote"


def test_toggle_takes_priority_over_mode(monkeypatch):
    controller = make_controller()
    t = [0.0]
    monkeypatch.setattr("controller.time.monotonic", lambda: t[0])

    set_toggle(controller, True)
    set_arrows(controller, left=True, right=False)
    controller.poll_events()  # 長押しタイマーの起点
    t[0] += LONG_PRESS_SECONDS + 0.1
    assert controller.poll_events() == "toggle_clock"
