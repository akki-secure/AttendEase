"""CoDroneEDUコントローラー接続とボタン入力の検知。"""

import time

from codrone_edu.drone import Drone

LONG_PRESS_SECONDS = 1.5
POLL_INTERVAL_SECONDS = 0.05


class Controller:
    def __init__(self) -> None:
        self.drone = Drone()
        self._toggle_pressed_since: float | None = None
        self._toggle_long_press_fired = False
        self._prev_left = False
        self._prev_right = False

    def connect(self, port: str | None = None) -> None:
        # 自動ペアリングは失敗しやすいため、CODRONE_PORT環境変数でCOMポートを指定できるようにする
        self.drone.pair(port)

    def close(self) -> None:
        self.drone.close()

    def _toggle_long_pressed_edge(self) -> bool:
        """Sボタンが長押しされた瞬間に1回だけTrueを返す。

        パワーボタンは電源管理を兼ねており、長押しするとコントローラーの
        画面が消灯し打刻フィードバック画像が表示されない事象を確認したため、
        Sボタンを打刻トリガーに使う。
        """
        if self.drone.s_pressed():
            if self._toggle_pressed_since is None:
                self._toggle_pressed_since = time.monotonic()
            held = time.monotonic() - self._toggle_pressed_since
            if held >= LONG_PRESS_SECONDS and not self._toggle_long_press_fired:
                self._toggle_long_press_fired = True
                return True
        else:
            self._toggle_pressed_since = None
            self._toggle_long_press_fired = False
        return False

    def _mode_switch_edge(self) -> str | None:
        """十字ボタン左右が押された瞬間に"office"/"remote"を返す(押しっぱなしでは連続発火しない)。"""
        left = self.drone.left_arrow_pressed()
        right = self.drone.right_arrow_pressed()
        event = None
        if left and not self._prev_left:
            event = "office"
        elif right and not self._prev_right:
            event = "remote"
        self._prev_left = left
        self._prev_right = right
        return event

    def poll_events(self):
        """1周期分ボタン状態を確認し、発生したイベント名(またはNone)を返す。呼び出し側でループさせる。"""
        if self._toggle_long_pressed_edge():
            return "toggle_clock"
        mode_event = self._mode_switch_edge()
        if mode_event is not None:
            return f"mode_{mode_event}"
        return None
