"""
メッセージテンプレート集
お肉膳スギモト 三井アウトレットパーク岡崎店
"""
from linebot.v3.messaging import (
    TextMessage,
    FlexMessage,
    FlexContainer,
    ImageMessage,
    StickerMessage,
)
import json


# ─────────────────────────────────────────
# 1. ウェルカムメッセージ（友だち追加時）
# ─────────────────────────────────────────

def welcome_messages(display_name: str = "") -> list:
    """友だち追加時のウェルカムメッセージ"""
    name_part = f"{display_name}さん、" if display_name else ""

    text_msg = TextMessage(
        text=(
            f"🥩 {name_part}お肉膳スギモトの\n"
            "LINE公式アカウントへようこそ！\n\n"
            "厳選した黒毛和牛を、\n"
            "職人の技と和の心でお届けします。\n\n"
            "友だち登録のお礼に、\n"
            "【初回来店限定クーポン】をプレゼント🎁\n"
            "↓下のカードをご確認ください"
        )
    )

    coupon_flex = welcome_coupon_flex()

    return [text_msg, coupon_flex]


def welcome_coupon_flex() -> FlexMessage:
    """初回来店クーポン（Flexメッセージ）"""
    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🎁 友だち登録特典",
                    "color": "#C9A84C",
                    "size": "sm",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": "初回来店クーポン",
                    "color": "#FFFFFF",
                    "size": "xl",
                    "weight": "bold"
                }
            ],
            "backgroundColor": "#1A1A1A",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "ドリンク1杯",
                    "size": "3xl",
                    "weight": "bold",
                    "color": "#8B0000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "無料サービス",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#333333",
                    "align": "center"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#C9A84C"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "【ご利用条件】",
                            "size": "sm",
                            "color": "#555555",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": "・初回ご来店時、お会計前にご提示ください\n・お1人様1回限り有効\n・他クーポンとの併用不可\n・有効期限：ご登録から30日間",
                            "size": "xs",
                            "color": "#777777",
                            "wrap": True
                        }
                    ]
                }
            ],
            "backgroundColor": "#FAFAFA",
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "お肉膳スギモト 三井アウトレットパーク岡崎店",
                    "size": "xs",
                    "color": "#C9A84C",
                    "align": "center"
                }
            ],
            "backgroundColor": "#1A1A1A",
            "paddingAll": "12px"
        }
    }

    return FlexMessage(
        alt_text="【初回来店クーポン】ドリンク1杯無料サービス",
        contents=FlexContainer.from_dict(bubble)
    )


# ─────────────────────────────────────────
# 2. 誕生日クーポン
# ─────────────────────────────────────────

def birthday_coupon_messages(display_name: str = "") -> list:
    """誕生日月の自動配信メッセージ"""
    name_part = f"{display_name}さん" if display_name else "あなた"

    text_msg = TextMessage(
        text=(
            f"🎂 {name_part}、\n"
            "お誕生日おめでとうございます！\n\n"
            "スギモトスタッフ一同、\n"
            "心よりお祝い申し上げます。\n\n"
            "素敵なお誕生日のお祝いに、\n"
            "特別なプレゼントをご用意しました🥩✨"
        )
    )

    coupon_flex = birthday_coupon_flex()

    return [text_msg, coupon_flex]


def birthday_coupon_flex() -> FlexMessage:
    """誕生日クーポン（Flexメッセージ）"""
    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🎂 誕生日月限定",
                    "color": "#C9A84C",
                    "size": "sm",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": "バースデークーポン",
                    "color": "#FFFFFF",
                    "size": "xl",
                    "weight": "bold"
                }
            ],
            "backgroundColor": "#8B0000",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "乾杯ドリンク1杯",
                    "size": "3xl",
                    "weight": "bold",
                    "color": "#8B0000",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "プレゼント🥂",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#333333",
                    "align": "center"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#C9A84C"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "【ご利用条件】",
                            "size": "sm",
                            "color": "#555555",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": "・誕生日月中にご来店時ご提示ください\n・お1人様1回限り有効\n・グループでのご来店時、ご本人のみ対象\n・他クーポンとの併用不可",
                            "size": "xs",
                            "color": "#777777",
                            "wrap": True
                        }
                    ]
                }
            ],
            "backgroundColor": "#FAFAFA",
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "お肉膳スギモト 三井アウトレットパーク岡崎店",
                    "size": "xs",
                    "color": "#C9A84C",
                    "align": "center"
                }
            ],
            "backgroundColor": "#1A1A1A",
            "paddingAll": "12px"
        }
    }

    return FlexMessage(
        alt_text="【誕生日月限定】乾杯ドリンク1杯プレゼント",
        contents=FlexContainer.from_dict(bubble)
    )


# ─────────────────────────────────────────
# 3. 一斉配信テンプレート
# ─────────────────────────────────────────

def new_menu_broadcast(menu_name: str, description: str, price: str) -> FlexMessage:
    """新メニュー告知（一斉配信用）"""
    bubble = {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🆕 NEW MENU",
                    "color": "#C9A84C",
                    "size": "lg",
                    "weight": "bold",
                    "align": "center"
                }
            ],
            "backgroundColor": "#1A1A1A",
            "paddingAll": "16px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": menu_name,
                    "size": "xl",
                    "weight": "bold",
                    "color": "#1A1A1A",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": description,
                    "size": "sm",
                    "color": "#555555",
                    "wrap": True,
                    "margin": "md"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#C9A84C"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": "価格",
                            "size": "sm",
                            "color": "#777777",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": price,
                            "size": "sm",
                            "color": "#8B0000",
                            "weight": "bold",
                            "flex": 2,
                            "align": "end"
                        }
                    ]
                }
            ],
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "メニューをもっと見る",
                        "uri": "https://line.me/R/ti/p/@sugimoto"  # 実際のURLに変更
                    },
                    "style": "primary",
                    "color": "#8B0000"
                }
            ],
            "paddingAll": "12px"
        }
    }

    return FlexMessage(
        alt_text=f"【新メニュー】{menu_name}",
        contents=FlexContainer.from_dict(bubble)
    )


def seasonal_campaign_broadcast(campaign_title: str, body_text: str, period: str) -> list:
    """
    季節キャンペーン告知テンプレート（テキスト + Flex）

    使用例:
        seasonal_campaign_broadcast(
            campaign_title="夏の黒毛和牛祭り",
            body_text="厳選された黒毛和牛A5ランクが今だけ特別価格で登場。...",
            period="2026年7月1日〜8月31日"
        )
    """
    text_msg = TextMessage(
        text=(
            f"🥩✨ {campaign_title} ✨🥩\n\n"
            f"{body_text}\n\n"
            f"📅 開催期間：{period}\n\n"
            "詳細はスタッフまでお気軽にお尋ねください。\n"
            "ご来店をスタッフ一同、心よりお待ちしております🙇‍♀️"
        )
    )

    return [text_msg]


def osusume_of_the_day(items: list[dict]) -> FlexMessage:
    """
    本日のおすすめ（カルーセル形式）

    items: [{"name": "...", "description": "...", "price": "..."}, ...]
    最大10品まで
    """
    bubbles = []
    for item in items[:10]:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🍖 本日のおすすめ",
                        "color": "#C9A84C",
                        "size": "xs"
                    }
                ],
                "backgroundColor": "#1A1A1A",
                "paddingAll": "12px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": item["name"],
                        "size": "md",
                        "weight": "bold",
                        "wrap": True,
                        "color": "#1A1A1A"
                    },
                    {
                        "type": "text",
                        "text": item.get("description", ""),
                        "size": "xs",
                        "color": "#777777",
                        "wrap": True,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": item.get("price", ""),
                        "size": "sm",
                        "color": "#8B0000",
                        "weight": "bold",
                        "margin": "md"
                    }
                ],
                "paddingAll": "16px"
            }
        }
        bubbles.append(bubble)

    carousel = {
        "type": "carousel",
        "contents": bubbles
    }

    return FlexMessage(
        alt_text="🍖 本日のおすすめメニューをご案内します",
        contents=FlexContainer.from_dict(carousel)
    )


# ─────────────────────────────────────────
# 4. 店舗情報
# ─────────────────────────────────────────

def store_info_message() -> FlexMessage:
    """店舗情報・アクセス"""
    bubble = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📍 店舗情報・アクセス",
                    "color": "#C9A84C",
                    "size": "md",
                    "weight": "bold"
                }
            ],
            "backgroundColor": "#1A1A1A",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "お肉膳スギモト",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#1A1A1A"
                },
                {
                    "type": "text",
                    "text": "三井アウトレットパーク岡崎店",
                    "size": "sm",
                    "color": "#555555"
                },
                {"type": "separator", "color": "#C9A84C"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "📍 住所", "size": "sm", "color": "#C9A84C", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "愛知県岡崎市\n三井アウトレットパーク岡崎内", "size": "sm", "color": "#333333", "flex": 5, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "🕐 営業時間", "size": "sm", "color": "#C9A84C", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "11:00〜21:00\n(L.O. 20:00)", "size": "sm", "color": "#333333", "flex": 5, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "📞 電話", "size": "sm", "color": "#C9A84C", "flex": 2, "weight": "bold"},
                                {"type": "text", "text": "※ショップ情報をご確認ください", "size": "sm", "color": "#333333", "flex": 5, "wrap": True}
                            ]
                        }
                    ]
                }
            ],
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "Googleマップで開く",
                        "uri": "https://maps.google.com/?q=三井アウトレットパーク岡崎"
                    },
                    "style": "primary",
                    "color": "#1A1A1A"
                }
            ],
            "paddingAll": "12px"
        }
    }

    return FlexMessage(
        alt_text="【店舗情報】お肉膳スギモト 三井アウトレットパーク岡崎店",
        contents=FlexContainer.from_dict(bubble)
    )


# ─────────────────────────────────────────
# 5. 誕生日登録ガイダンス
# ─────────────────────────────────────────

BIRTHDAY_REGISTER_PROMPT = """🎂 誕生日を登録して、
特別なプレゼントをお受け取りください🎁

誕生日月に、乾杯ドリンクを
1杯プレゼントいたします🥂

━━━━━━━━━━━━━━━
📝 登録方法
「誕生日 〇月〇日」の形式で
メッセージを送信してください

（例）誕生日 3月15日
━━━━━━━━━━━━━━━

※誕生日は年を除いた月・日のみ
　登録いたします（個人情報保護のため）"""


# ─────────────────────────────────────────
# 6. スタンプ特典通知
# ─────────────────────────────────────────

def stamp_reward_message(stamp_count: int) -> TextMessage:
    """スタンプ特典達成時の通知"""
    rewards = {
        5: ("🍮 デザート1品サービス",
            "次回ご来店時に、デザートを1品サービスいたします！\nスタッフにこのメッセージをご提示ください。"),
        10: ("🏷️ 次回10%オフクーポン",
             "次回ご来店時に、お会計から10%オフにいたします！\nスタッフにこのメッセージをご提示ください。"),
        20: ("🥩 特選肉1品プレゼント（VIP特典）",
             "常連のお客様への感謝を込めて、\n特選肉を1品プレゼントいたします！\nご来店時にスタッフまでお申し付けください。"),
    }

    if stamp_count in rewards:
        reward_name, reward_detail = rewards[stamp_count]
        return TextMessage(
            text=(
                f"🎊 おめでとうございます！\n\n"
                f"スタンプが{stamp_count}個に達しました！\n\n"
                f"【特典】{reward_name}\n\n"
                f"{reward_detail}\n\n"
                f"いつもご来店いただき、\n"
                f"ありがとうございます🙇‍♀️"
            )
        )
    return None
