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
    """出勤: ドアに向かって歩き、入っていく人物のシルエット(退勤アイコンと対になる構図)。"""
    img, draw = _new_canvas()

    # 歩く人物(左側、ドアに向かって右へ進む)
    # 頭
    draw.ellipse((18, 6, 32, 20), fill=SILHOUETTE)
    # 胴体(進行方向へ前傾)
    draw.polygon([(30, 20), (16, 22), (18, 40), (28, 40)], fill=SILHOUETTE)
    # 前に伸ばした腕(ドア方向)
    draw.line((18, 24, 2, 18), fill=SILHOUETTE, width=4)
    # 後ろに引いた腕
    draw.line((28, 24, 40, 32), fill=SILHOUETTE, width=4)
    # 蹴り出した前足(地面から浮いている)
    draw.line((22, 40, 6, 48), fill=SILHOUETTE, width=5)
    # 地面に着いた後ろ足
    draw.line((26, 40, 36, 58), fill=SILHOUETTE, width=5)

    # 入室方向の矢印
    draw.line((46, 32, 78, 32), fill=SILHOUETTE, width=4)
    draw.polygon([(78, 32), (70, 26), (70, 40)], fill=SILHOUETTE)

    # ドア枠(入っていく先)
    draw.rectangle((92, 6, 124, 58), outline=SILHOUETTE, width=3)

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
