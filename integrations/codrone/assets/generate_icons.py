"""コントローラーディスプレイ用の出勤/退勤シルエットアイコンを生成するスクリプト。

CoDroneEDU SDKの get_image_data() は画像を127x63にリサイズしたうえで、
明度200を閾値に「明るい=背景(非表示)」「暗い=黒ドット」として二値描画する
(_controller_draw_image_desktop の実装で確認済み)。そのためアイコンは
あらかじめ白背景+黒シルエットで127x63ぴったりに作成しておく。

再生成する場合: python assets/generate_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

CONTROLLER_WIDTH = 127
CONTROLLER_HEIGHT = 63

ASSETS_DIR = Path(__file__).parent
BACKGROUND = (255, 255, 255)
SILHOUETTE = (0, 0, 0)


def _new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (CONTROLLER_WIDTH, CONTROLLER_HEIGHT), BACKGROUND)
    return img, ImageDraw.Draw(img)


def build_clock_in_image() -> Image.Image:
    """出勤: 歩く人物のシルエット。"""
    img, draw = _new_canvas()

    # 頭
    draw.ellipse((52, 6, 66, 20), fill=SILHOUETTE)
    # 胴体(前傾)
    draw.polygon([(56, 20), (68, 22), (66, 40), (54, 40)], fill=SILHOUETTE)
    # 前に伸ばした腕
    draw.line((66, 24, 84, 30), fill=SILHOUETTE, width=4)
    # 後ろに引いた腕
    draw.line((56, 24, 42, 34), fill=SILHOUETTE, width=4)
    # 前に出した足
    draw.line((62, 40, 78, 56), fill=SILHOUETTE, width=5)
    # 後ろの足
    draw.line((58, 40, 46, 58), fill=SILHOUETTE, width=5)

    return img


def build_clock_out_image() -> Image.Image:
    """退勤: ドアから退室する人物のシルエット。"""
    img, draw = _new_canvas()

    # ドア枠
    draw.rectangle((10, 6, 46, 58), outline=SILHOUETTE, width=3)
    # 退室方向の矢印
    draw.line((54, 32, 90, 32), fill=SILHOUETTE, width=4)
    draw.polygon([(90, 32), (80, 24), (80, 40)], fill=SILHOUETTE)

    # 退室する人物(ドアの右側、歩くポーズ)
    draw.ellipse((96, 8, 108, 20), fill=SILHOUETTE)
    draw.polygon([(99, 20), (109, 22), (107, 38), (97, 38)], fill=SILHOUETTE)
    draw.line((107, 24, 120, 20), fill=SILHOUETTE, width=4)
    draw.line((99, 24, 90, 30), fill=SILHOUETTE, width=4)
    draw.line((104, 38, 116, 54), fill=SILHOUETTE, width=5)
    draw.line((100, 38, 92, 56), fill=SILHOUETTE, width=5)

    return img


def main() -> None:
    clock_in_path = ASSETS_DIR / "clock_in.png"
    clock_out_path = ASSETS_DIR / "clock_out.png"
    build_clock_in_image().save(clock_in_path)
    build_clock_out_image().save(clock_out_path)
    print(f"生成しました: {clock_in_path}")
    print(f"生成しました: {clock_out_path}")


if __name__ == "__main__":
    main()
