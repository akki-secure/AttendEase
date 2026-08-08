"""ディスプレイ表示の切り分け用の一時的な診断スクリプト。
問題が特定できたら削除すること。
"""

from codrone_edu.drone import Drone

import feedback

drone = Drone()
drone.pair()

pixel_list = drone.get_image_data(str(feedback.CLOCK_IN_IMAGE_PATH))
print("pixel_list:", type(pixel_list), len(pixel_list) if pixel_list else None)

drone.controller_draw_image(pixel_list)
print("描画コマンドを送信しました。画面を見てください。")

input("Enterで終了...")
drone.close()
