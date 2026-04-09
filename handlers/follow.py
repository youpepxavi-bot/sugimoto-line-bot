"""
友だち追加（Follow）イベントハンドラー
- ウェルカムメッセージ送信
- ユーザーDB登録
"""
import logging
from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
)
from linebot.v3.webhooks import FollowEvent
from database import upsert_user
from templates.messages import welcome_messages

logger = logging.getLogger(__name__)


async def handle_follow(event: FollowEvent, api_client: ApiClient, db):
    """友だち追加時の処理"""
    line_api = MessagingApi(api_client)
    user_id = event.source.user_id

    # ユーザー情報取得（表示名）
    display_name = ""
    try:
        profile = line_api.get_profile(user_id)
        display_name = profile.display_name or ""
    except Exception as e:
        logger.warning(f"プロフィール取得失敗 user_id={user_id}: {e}")

    # DBに登録
    try:
        upsert_user(db, user_id, display_name)
        logger.info(f"新規ユーザー登録: {user_id} ({display_name})")
    except Exception as e:
        logger.error(f"ユーザー登録エラー: {e}")

    # ウェルカムメッセージ送信
    messages = welcome_messages(display_name)
    try:
        line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )
    except Exception as e:
        logger.error(f"ウェルカムメッセージ送信エラー: {e}")
