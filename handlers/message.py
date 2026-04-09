"""
テキストメッセージハンドラー
- 誕生日登録（「誕生日 〇月〇日」形式）
- その他メッセージへの応答
"""
import re
import logging
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent
from database import set_birthday
from templates.messages import BIRTHDAY_REGISTER_PROMPT

logger = logging.getLogger(__name__)

# 誕生日パターン: 「誕生日 3月15日」「誕生日 03月05日」など
BIRTHDAY_PATTERN = re.compile(
    r"誕生日[\s　]*(\d{1,2})月[\s　]*(\d{1,2})日"
)


async def handle_message(event: MessageEvent, api_client: ApiClient, db):
    """テキストメッセージ受信時の処理"""
    line_api = MessagingApi(api_client)
    user_id = event.source.user_id
    text = event.message.text.strip()
    reply_token = event.reply_token

    reply_messages = []

    # ──────────────────────────────────
    # 誕生日登録
    # ──────────────────────────────────
    birthday_match = BIRTHDAY_PATTERN.search(text)
    if birthday_match:
        month = int(birthday_match.group(1))
        day = int(birthday_match.group(2))

        # バリデーション
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                set_birthday(db, user_id, month, day)
                reply_messages = [
                    TextMessage(
                        text=(
                            f"🎂 誕生日を登録しました！\n\n"
                            f"📅 {month}月{day}日\n\n"
                            f"誕生日月に、特別なクーポンを\n"
                            f"お送りします🎁\n\n"
                            f"ご来店をお待ちしております🥩"
                        )
                    )
                ]
                logger.info(f"誕生日登録: {user_id} → {month}月{day}日")
            except Exception as e:
                logger.error(f"誕生日登録エラー: {e}")
                reply_messages = [TextMessage(text="登録中にエラーが発生しました。\nしばらくしてから再度お試しください。")]
        else:
            reply_messages = [
                TextMessage(
                    text=(
                        "⚠️ 日付の形式が正しくありません。\n\n"
                        "「誕生日 〇月〇日」の形式で\nご入力ください。\n\n"
                        "（例）誕生日 3月15日"
                    )
                )
            ]

    # ──────────────────────────────────
    # 誕生日という単語だけ（登録ガイダンス）
    # ──────────────────────────────────
    elif "誕生日" in text and "登録" in text:
        reply_messages = [TextMessage(text=BIRTHDAY_REGISTER_PROMPT)]

    # ──────────────────────────────────
    # キーワード応答
    # ──────────────────────────────────
    elif any(kw in text for kw in ["クーポン", "coupon", "割引"]):
        from templates.messages import welcome_coupon_flex
        reply_messages = [
            TextMessage(text="クーポンのご案内です🎁"),
            welcome_coupon_flex()
        ]

    elif any(kw in text for kw in ["店舗", "アクセス", "場所", "住所", "営業時間"]):
        from templates.messages import store_info_message
        reply_messages = [store_info_message()]

    elif any(kw in text for kw in ["メニュー", "おすすめ", "何がある"]):
        reply_messages = [
            TextMessage(
                text=(
                    "🍖 メニューのお問い合わせは\n"
                    "リッチメニューの「おすすめ・メニュー」を\n"
                    "タップしてご確認ください。\n\n"
                    "また、ご来店時にスタッフへ\n"
                    "お気軽にご相談ください😊"
                )
            )
        ]

    elif any(kw in text for kw in ["予約", "席", "テーブル"]):
        reply_messages = [
            TextMessage(
                text=(
                    "ご予約のお問い合わせ、\nありがとうございます。\n\n"
                    "お電話またはネット予約サイトより\nご予約いただけます。\n\n"
                    "📍 三井アウトレットパーク岡崎店内\n"
                    "スタッフ一同、心よりお待ちしております🙇‍♀️"
                )
            )
        ]

    else:
        # デフォルト応答
        reply_messages = [
            TextMessage(
                text=(
                    "メッセージをありがとうございます😊\n\n"
                    "下のメニューからご希望の項目を\nお選びください。\n\n"
                    "ご不明な点はスタッフまで\nお気軽にご連絡ください。"
                )
            )
        ]

    if reply_messages:
        try:
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=reply_messages
                )
            )
        except Exception as e:
            logger.error(f"リプライ送信エラー: {e}")
