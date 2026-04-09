"""
リッチメニュー画像生成 + LINE API設定スクリプト
お肉膳スギモト 三井アウトレットパーク岡崎店

【実行方法】
    python generate_richmenu.py --generate-image   # 画像のみ生成
    python generate_richmenu.py --setup-all        # 画像生成 + LINE API設定まで全自動

【前提条件】
    .env に LINE_CHANNEL_ACCESS_TOKEN が設定されていること
    pip install Pillow line-bot-sdk python-dotenv
"""
import os
import sys
import io
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Windows コンソール出力のエンコーディング問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─────────────────────────────────────────
# 画像生成（Pillow）
# ─────────────────────────────────────────

def generate_rich_menu_image(output_path: str = "richmenu.png"):
    """
    2500×1686px のリッチメニュー画像を生成
    カラースキーム: 黒・金・深紅
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ Pillow がインストールされていません: pip install Pillow")
        sys.exit(1)

    W, H = 2500, 1686
    COLS, ROWS = 3, 2
    CELL_W = W // COLS   # 833px
    CELL_H = H // ROWS   # 843px

    # ─── カラー定義 ───
    BG_COLOR      = (18, 18, 18)       # ほぼ黒
    BORDER_COLOR  = (201, 168, 76)     # 金色
    CRIMSON       = (139, 0, 0)        # 深紅
    GOLD          = (201, 168, 76)
    WHITE         = (255, 255, 255)
    LIGHT_GRAY    = (200, 200, 200)
    CELL_BG       = (28, 28, 28)       # 少し明るい黒

    # ─── ボタン定義 ───
    # アイコンは漢字1文字（Pillowの絵文字非対応を回避）
    buttons = [
        # Row 1
        {
            "icon": "割",
            "main":  "クーポンを",
            "sub":   "受け取る",
            "color": CRIMSON,
            "accent": GOLD,
        },
        {
            "icon": "印",
            "main":  "スタンプ",
            "sub":   "カード",
            "color": GOLD,
            "accent": WHITE,
        },
        {
            "icon": "位",
            "main":  "人気メニュー",
            "sub":   "ランキング",
            "color": CRIMSON,
            "accent": GOLD,
        },
        # Row 2
        {
            "icon": "試",
            "main":  "先行試食",
            "sub":   "チケット",
            "color": GOLD,
            "accent": WHITE,
        },
        {
            "icon": "報",
            "main":  "お知らせ",
            "sub":   "",
            "color": CRIMSON,
            "accent": GOLD,
        },
        {
            "icon": "店",
            "main":  "店舗情報・",
            "sub":   "アクセス",
            "color": GOLD,
            "accent": WHITE,
        },
    ]

    # ─── フォント設定 ───
    font_candidates = [
        "C:/Windows/Fonts/YuGothB.ttc",        # Yu Gothic Bold
        "C:/Windows/Fonts/YuGothM.ttc",        # Yu Gothic Medium
        "C:/Windows/Fonts/meiryo.ttc",          # Meiryo
        "C:/Windows/Fonts/msgothic.ttc",        # MS Gothic
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",  # macOS
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",  # Linux
    ]

    font_path = None
    for fp in font_candidates:
        if os.path.exists(fp):
            font_path = fp
            print(f"✅ フォント: {fp}")
            break

    def load_font(size: int):
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    font_icon  = load_font(160)
    font_main  = load_font(90)
    font_sub   = load_font(65)
    font_title = load_font(42)

    # ─── キャンバス作成 ───
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 背景グラデーション風の縦ライン（装飾）
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(25, 25, 25), width=1)

    # ─── 各セルを描画 ───
    for idx, btn in enumerate(buttons):
        col = idx % COLS
        row = idx // COLS

        x0 = col * CELL_W
        y0 = row * CELL_H
        x1 = x0 + CELL_W
        y1 = y0 + CELL_H

        cx = x0 + CELL_W // 2  # セル中央X
        cy = y0 + CELL_H // 2  # セル中央Y

        # セル背景
        draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=CELL_BG)

        # 上部アクセントバー
        bar_color = btn["color"]
        draw.rectangle([x0 + 2, y0 + 2, x1 - 2, y0 + 14], fill=bar_color)

        # アイコン背景円
        circle_r = 110
        circle_y = y0 + CELL_H // 3
        draw.ellipse(
            [cx - circle_r, circle_y - circle_r,
             cx + circle_r, circle_y + circle_r],
            fill=(35, 35, 35),
            outline=btn["accent"],
            width=3
        )

        # アイコン（テキスト）
        try:
            icon_bbox = draw.textbbox((0, 0), btn["icon"], font=font_icon)
            icon_w = icon_bbox[2] - icon_bbox[0]
            icon_h = icon_bbox[3] - icon_bbox[1]
            draw.text(
                (cx - icon_w // 2, circle_y - icon_h // 2 - 10),
                btn["icon"],
                font=font_icon,
                fill=btn["accent"]
            )
        except Exception:
            # フォールバック（絵文字非対応の場合）
            draw.text(
                (cx - 40, circle_y - 40),
                "◆",
                font=font_main,
                fill=btn["color"]
            )

        # メインラベル
        try:
            main_bbox = draw.textbbox((0, 0), btn["main"], font=font_main)
            main_w = main_bbox[2] - main_bbox[0]
            draw.text(
                (cx - main_w // 2, y0 + CELL_H * 2 // 3 - 10),
                btn["main"],
                font=font_main,
                fill=WHITE
            )
        except Exception:
            pass

        # サブラベル
        if btn["sub"]:
            try:
                sub_bbox = draw.textbbox((0, 0), btn["sub"], font=font_sub)
                sub_w = sub_bbox[2] - sub_bbox[0]
                draw.text(
                    (cx - sub_w // 2, y0 + CELL_H * 2 // 3 + 90),
                    btn["sub"],
                    font=font_sub,
                    fill=LIGHT_GRAY
                )
            except Exception:
                pass

        # 下部装飾ライン
        draw.rectangle(
            [x0 + 40, y1 - 20, x1 - 40, y1 - 14],
            fill=btn["accent"]
        )

    # ─── グリッド線（セル境界） ───
    border_w = 3

    # 縦線（2本）
    for c in range(1, COLS):
        x = c * CELL_W
        draw.rectangle([x - border_w, 0, x + border_w, H], fill=GOLD)

    # 横線（1本）
    y = CELL_H
    draw.rectangle([0, y - border_w, W, y + border_w], fill=GOLD)

    # 外枠
    draw.rectangle([0, 0, W - 1, H - 1], outline=GOLD, width=6)

    # ─── 店名（中央上部） ───
    store_name = "お肉膳スギモト"
    try:
        nm_bbox = draw.textbbox((0, 0), store_name, font=font_title)
        nm_w = nm_bbox[2] - nm_bbox[0]
        # 横ライン上に店名を重ねる（中央）
        text_x = W // 2 - nm_w // 2
        text_y = CELL_H - font_title.size // 2 - 6
        # 背景パッチ
        draw.rectangle(
            [text_x - 20, text_y - 4, text_x + nm_w + 20, text_y + font_title.size + 4],
            fill=GOLD
        )
        draw.text((text_x, text_y), store_name, font=font_title, fill=BG_COLOR)
    except Exception:
        pass

    # ─── 保存 ───
    img.save(output_path, "PNG", optimize=True)
    size_kb = os.path.getsize(output_path) // 1024
    print(f"✅ リッチメニュー画像を生成しました: {output_path} ({size_kb} KB)")
    print(f"   サイズ: {W}×{H}px")
    return output_path


# ─────────────────────────────────────────
# LINE API: リッチメニュー設定
# ─────────────────────────────────────────

def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_rich_menu(token: str) -> str:
    """リッチメニューを作成してIDを返す"""
    W, H = 2500, 1686
    COLS, ROWS = 3, 2
    CELL_W = W // COLS
    CELL_H = H // ROWS

    rich_menu = {
        "size": {"width": W, "height": H},
        "selected": True,
        "name": "スギモト メインメニュー",
        "chatBarText": "メニューを開く",
        "areas": [
            # Row 1
            {
                "bounds": {"x": 0,         "y": 0,      "width": CELL_W, "height": CELL_H},
                "action": {"type": "postback", "data": "action=coupon",     "label": "クーポンを受け取る"}
            },
            {
                "bounds": {"x": CELL_W,    "y": 0,      "width": CELL_W, "height": CELL_H},
                "action": {"type": "postback", "data": "action=stamp",      "label": "スタンプカード"}
            },
            {
                "bounds": {"x": CELL_W*2,  "y": 0,      "width": CELL_W, "height": CELL_H},
                "action": {"type": "postback", "data": "action=menu",       "label": "人気メニューランキング"}
            },
            # Row 2
            {
                "bounds": {"x": 0,         "y": CELL_H, "width": CELL_W, "height": CELL_H},
                "action": {"type": "postback", "data": "action=birthday",   "label": "先行試食チケット"}
            },
            {
                "bounds": {"x": CELL_W,    "y": CELL_H, "width": CELL_W, "height": CELL_H},
                "action": {"type": "postback", "data": "action=news",       "label": "お知らせ"}
            },
            {
                "bounds": {"x": CELL_W*2,  "y": CELL_H, "width": CELL_W, "height": CELL_H},
                "action": {"type": "postback", "data": "action=store_info", "label": "店舗情報・アクセス"}
            },
        ]
    }

    resp = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers={**get_headers(token), "Content-Type": "application/json"},
        data=json.dumps(rich_menu)
    )
    resp.raise_for_status()
    rich_menu_id = resp.json()["richMenuId"]
    print(f"✅ リッチメニュー作成完了: {rich_menu_id}")
    return rich_menu_id


def upload_rich_menu_image(token: str, rich_menu_id: str, image_path: str):
    """リッチメニュー画像をアップロード"""
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers={**get_headers(token), "Content-Type": "image/png"},
            data=f
        )
    resp.raise_for_status()
    print(f"✅ 画像アップロード完了")


def set_default_rich_menu(token: str, rich_menu_id: str):
    """デフォルトリッチメニューに設定"""
    resp = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=get_headers(token)
    )
    resp.raise_for_status()
    print(f"✅ デフォルトリッチメニューに設定完了")


def delete_existing_rich_menus(token: str):
    """既存のリッチメニューを全削除（クリーンアップ）"""
    resp = requests.get(
        "https://api.line.me/v2/bot/richmenu/list",
        headers=get_headers(token)
    )
    resp.raise_for_status()
    menus = resp.json().get("richmenus", [])

    if not menus:
        print("既存のリッチメニューなし")
        return

    for menu in menus:
        mid = menu["richMenuId"]
        requests.delete(
            f"https://api.line.me/v2/bot/richmenu/{mid}",
            headers=get_headers(token)
        )
        print(f"🗑️  削除: {mid}")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="お肉膳スギモト リッチメニュー設定ツール"
    )
    parser.add_argument(
        "--generate-image", action="store_true",
        help="リッチメニュー画像のみ生成（API設定なし）"
    )
    parser.add_argument(
        "--setup-all", action="store_true",
        help="画像生成 + LINE API設定を全自動で実行"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="既存リッチメニューを削除してから設定"
    )
    parser.add_argument(
        "--output", default="richmenu.png",
        help="出力画像ファイル名（デフォルト: richmenu.png）"
    )
    args = parser.parse_args()

    if not args.generate_image and not args.setup_all:
        parser.print_help()
        return

    # 画像生成
    image_path = generate_rich_menu_image(args.output)

    if args.setup_all:
        token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
        if not token:
            print("❌ LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
            sys.exit(1)

        print("\n📡 LINE API設定を開始します...\n")

        if args.clean:
            print("🗑️  既存リッチメニューを削除中...")
            delete_existing_rich_menus(token)

        rich_menu_id = create_rich_menu(token)
        upload_rich_menu_image(token, rich_menu_id, image_path)
        set_default_rich_menu(token, rich_menu_id)

        print(f"\n🎉 リッチメニュー設定完了！")
        print(f"   Rich Menu ID: {rich_menu_id}")
        print(f"\nLINE Official Account Manager でも確認できます。")


if __name__ == "__main__":
    main()
