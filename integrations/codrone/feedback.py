"""CoDroneEDUコントローラーで出勤・退勤時の音・LED・ディスプレイ表示を行うモジュール。"""

from pathlib import Path

from codrone_edu.drone import Drone

# 出勤: 上昇するメロディ(始まりを表す明るい音)
CLOCK_IN_NOTES = [(523, 150), (659, 150), (784, 250)]  # C5 -> E5 -> G5

# 退勤: 下降するメロディ(締めくくりを表す落ち着いた音)
CLOCK_OUT_NOTES = [(784, 150), (659, 150), (523, 250)]  # G5 -> E5 -> C5

ASSETS_DIR = Path(__file__).parent / "assets"
CLOCK_IN_IMAGE_PATH = ASSETS_DIR / "clock_in.png"
CLOCK_OUT_IMAGE_PATH = ASSETS_DIR / "clock_out.png"


def play_clock_in_sound(drone: Drone) -> None:
    for note, duration in CLOCK_IN_NOTES:
        drone.controller_buzzer(note, duration)


def play_clock_out_sound(drone: Drone) -> None:
    for note, duration in CLOCK_OUT_NOTES:
        drone.controller_buzzer(note, duration)


def play_error_sound(drone: Drone) -> None:
    drone.controller_buzzer(200, 400)


def led_office(drone: Drone) -> None:
    drone.set_controller_LED(0, 0, 255, 150)  # 青


def led_remote(drone: Drone) -> None:
    drone.set_controller_LED(0, 255, 0, 150)  # 緑


def led_success(drone: Drone) -> None:
    drone.set_controller_LED(0, 255, 0, 255)


def led_error(drone: Drone) -> None:
    drone.set_controller_LED(255, 0, 0, 255)


def show_clock_in_image(drone: Drone) -> None:
    _draw_image_on_controller(drone, CLOCK_IN_IMAGE_PATH)


def show_clock_out_image(drone: Drone) -> None:
    _draw_image_on_controller(drone, CLOCK_OUT_IMAGE_PATH)


def _draw_image_on_controller(drone: Drone, image_path: Path) -> None:
    """コントローラーのディスプレイに画像を描画する。

    get_image_data()がファイルを127x63にリサイズし、
    controller_draw_image()が明度を閾値に二値描画する(SDK側の仕様)。
    表示に失敗しても打刻自体は成功しているため、例外は握りつぶし警告のみ出す。
    """
    try:
        pixel_list = drone.get_image_data(str(image_path))
        drone.controller_draw_image(pixel_list)
    except Exception as e:
        print(f"ディスプレイ表示に失敗しました: {e}")


if __name__ == "__main__":
    drone = Drone()
    drone.pair()
    try:
        print("出勤音を再生します...")
        play_clock_in_sound(drone)
        print("退勤音を再生します...")
        play_clock_out_sound(drone)
    finally:
        drone.close()
