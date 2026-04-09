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
    meat_lineup_message,
    popular_menu_ranking,
    senkoh_shishoku_ticket,
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
        messages = [
            TextMessage(text="🏆 人気メニューランキングをご案内します\n\nお客様に特に選ばれている一品をご覧ください✨"),
            popular_menu_ranking()
        ]

    elif data == "action=birthday":
        messages = [
            TextMessage(text="🥩 LINE会員限定の先行試食チケットです！\n\n新メニューをいち早く無料でお試しいただけます。\nご来店の際にスタッフへご提示ください🎁"),
            senkoh_shishoku_ticket()
        ]

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
        messages = [
            TextMessage(text="🥩 スギモトこだわりの上質お肉をご紹介します\n\n厳選素材の数々をぜひご堪能ください✨"),
            meat_lineup_message()
        ]

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
