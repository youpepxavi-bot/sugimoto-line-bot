"""
ポストバックイベントハンドラー（リッチメニューボタン押下）
各ボタンのアクションに対応する処理
"""
import logging
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import PostbackEvent
from templates.messages import (
    welcome_coupon_flex,
    store_info_message,
    osusume_of_the_day,
    BIRTHDAY_REGISTER_PROMPT,
)

logger = logging.getLogger(__name__)

# リッチメニューの各ボタンに設定するpostback data
POSTBACK_ACTIONS = {
    "action=coupon":      "クーポン表示",
    "action=stamp":       "スタンプカード案内",
    "action=menu":        "本日のおすすめ表示",
    "action=birthday":    "誕生日登録案内",
    "action=news":        "お知らせ表示",
    "action=store_info":  "店舗情報表示",
}


async def handle_postback(event: PostbackEvent, api_client: ApiClient, db):
    """リッチメニューボタン押下時の処理"""
    line_api = MessagingApi(api_client)
    data = event.postback.data
    reply_token = event.reply_token

    logger.info(f"Postback受信: {data}")

    messages = []

    if data == "action=coupon":
        messages = [
            TextMessage(text="クーポンをご用意しました🎁\nご来店時にスタッフへご提示ください。"),
            welcome_coupon_flex()
        ]

    elif data == "action=stamp":
        messages = [
            TextMessage(
                text=(
                    "🎴 スタンプカードのご案内\n\n"
                    "ご来店1回につきスタンプ1個をプレゼント！\n\n"
                    "【特典】\n"
                    "🏅 5スタンプ　→ デザート1品サービス\n"
                    "🥈 10スタンプ → 次回10%オフ\n"
                    "🥇 20スタンプ → 特選肉1品プレゼント\n"
                    "（VIP常連様限定特典）\n\n"
                    "スタンプはLINEショップカードにて\n"
                    "管理・付与いたします。\n"
                    "来店時にスタッフへお声がけください！"
                )
            )
        ]

    elif data == "action=menu":
        # 本日のおすすめ（実際は管理画面やDBから取得する想定）
        sample_items = [
            {
                "name": "黒毛和牛 特上カルビ",
                "description": "口の中でとろける霜降りの旨み。炭火でじっくり焼き上げた極上の一品。",
                "price": "3,300円（税込）"
            },
            {
                "name": "特選タン塩",
                "description": "厚切りで提供する希少部位のタン。レモンを絞ってどうぞ。",
                "price": "2,200円（税込）"
            },
            {
                "name": "和牛ミスジ",
                "description": "1頭から少量しか取れない希少部位。なめらかな食感とコクが絶品。",
                "price": "2,750円（税込）"
            },
        ]
        messages = [
            TextMessage(text="🍖 本日のおすすめをご案内します\n\nスタッフもイチオシの品々です✨"),
            osusume_of_the_day(sample_items)
        ]

    elif data == "action=birthday":
        messages = [TextMessage(text=BIRTHDAY_REGISTER_PROMPT)]

    elif data == "action=news":
        messages = [
            TextMessage(
                text=(
                    "📢 最新のお知らせ\n\n"
                    "現在、新着のお知らせはございません。\n\n"
                    "イベントやキャンペーン情報は\n"
                    "LINEでお知らせしますので、\n"
                    "お楽しみにお待ちください🥩✨"
                )
            )
        ]

    elif data == "action=store_info":
        messages = [store_info_message()]

    else:
        logger.warning(f"未定義のpostback data: {data}")
        messages = [TextMessage(text="ご選択ありがとうございます。\n詳しくはスタッフまでお声がけください。")]

    if messages:
        try:
            line_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=messages
                )
            )
        except Exception as e:
            logger.error(f"リプライ送信エラー: {e}")
