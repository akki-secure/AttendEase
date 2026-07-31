"""CoDroneEDUコントローラーでAttendEaseに打刻するブリッジ本体。"""

import time

import feedback
from api_client import AttendEaseClient
from controller import POLL_INTERVAL_SECONDS, Controller


def main() -> None:
    client = AttendEaseClient()
    client.ensure_logged_in()

    controller = Controller()
    print("コントローラーとペアリングしています...")
    controller.connect()
    print("接続完了。パワーボタン長押しで出勤/退勤、十字ボタン左右で出社/リモート切り替え。")

    work_type = "office"
    feedback.led_office(controller.drone)

    try:
        while True:
            event = controller.poll_events()

            if event == "mode_office":
                work_type = "office"
                feedback.led_office(controller.drone)
                print("出社モードに切り替えました。")
            elif event == "mode_remote":
                work_type = "remote"
                feedback.led_remote(controller.drone)
                print("リモートモードに切り替えました。")
            elif event == "toggle_clock":
                _handle_toggle_clock(client, controller.drone, work_type)

            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("終了します。")
    finally:
        controller.close()


def _handle_toggle_clock(client: AttendEaseClient, drone, work_type: str) -> None:
    try:
        status = client.get_today_status()
        if status["status"] == "NOT_CLOCKED_IN":
            client.clock_in(work_type)
            feedback.play_clock_in_sound(drone)
            print(f"出勤を記録しました({work_type})。")
        else:
            client.clock_out()
            feedback.play_clock_out_sound(drone)
            print("退勤を記録しました。")
    except Exception as e:
        feedback.led_error(drone)
        feedback.play_error_sound(drone)
        print(f"打刻に失敗しました: {e}")


if __name__ == "__main__":
    main()
