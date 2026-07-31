"""CoDroneEDUコントローラーで出勤・退勤時の音を鳴らすモジュール。"""

from codrone_edu.drone import Drone

# 出勤: 上昇するメロディ(始まりを表す明るい音)
CLOCK_IN_NOTES = [(523, 150), (659, 150), (784, 250)]  # C5 -> E5 -> G5

# 退勤: 下降するメロディ(締めくくりを表す落ち着いた音)
CLOCK_OUT_NOTES = [(784, 150), (659, 150), (523, 250)]  # G5 -> E5 -> C5


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
