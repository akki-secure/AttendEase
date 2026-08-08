"""feedback.pyのディスプレイ表示ロジックのテスト(実機・実SDK不要)。"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import feedback  # noqa: E402


def test_show_clock_in_image_calls_get_image_data_and_draw():
    drone = MagicMock()
    drone.get_image_data.return_value = ["pixel_data"]

    feedback.show_clock_in_image(drone)

    drone.get_image_data.assert_called_once_with(str(feedback.CLOCK_IN_IMAGE_PATH))
    drone.controller_draw_image.assert_called_once_with(["pixel_data"])


def test_show_clock_out_image_calls_get_image_data_and_draw():
    drone = MagicMock()
    drone.get_image_data.return_value = ["pixel_data"]

    feedback.show_clock_out_image(drone)

    drone.get_image_data.assert_called_once_with(str(feedback.CLOCK_OUT_IMAGE_PATH))
    drone.controller_draw_image.assert_called_once_with(["pixel_data"])


def test_show_clock_in_image_display_failure_does_not_raise():
    drone = MagicMock()
    drone.get_image_data.side_effect = Exception("display error")

    feedback.show_clock_in_image(drone)  # 例外が伝播しなければOK


def test_show_clock_out_image_display_failure_does_not_raise():
    drone = MagicMock()
    drone.controller_draw_image.side_effect = Exception("display error")

    feedback.show_clock_out_image(drone)  # 例外が伝播しなければOK


def test_image_assets_exist():
    assert feedback.CLOCK_IN_IMAGE_PATH.exists()
    assert feedback.CLOCK_OUT_IMAGE_PATH.exists()
