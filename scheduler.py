"""
誕生日クーポン自動配信スケジューラー
APScheduler を使用して毎日09:00に実行
"""
import os
import logging
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
)
from database import SessionLocal, get_birthday_targets, mark_birthday_coupon_sent
from templates.messages import birthday_coupon_messages

logger = logging.getLogger(__name__)


def get_line_api_client() -> ApiClient:
    """LINE API クライアントを取得"""
    configuration = Configuration(
        access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    )
    return ApiClient(configuration)


async def send_birthday_coupons():
    """
    誕生日クーポン自動配信
    毎日09:00に実行し、誕生日が今日のユーザーへクーポンを送信
    """
    today = date.today()
    month = today.month
    day = today.day
    year = today.year

    logger.info(f"誕生日クーポン配信チェック開始: {today}")

    db = SessionLocal()
    try:
        targets = get_birthday_targets(db, month, day, year)

        if not targets:
            logger.info("本日の誕生日対象者なし")
            return

        logger.info(f"誕生日対象者: {len(targets)}名")

        with get_line_api_client() as api_client:
            line_api = MessagingApi(api_client)

            for user in targets:
                try:
                    messages = birthday_coupon_messages(user.display_name or "")

                    line_api.push_message(
                        PushMessageRequest(
                            to=user.line_user_id,
                            messages=messages
                        )
                    )

                    # 送信済みフラグを更新
                    mark_birthday_coupon_sent(db, user.line_user_id, year)

                    logger.info(
                        f"誕生日クーポン送信完了: "
                        f"{user.line_user_id} ({user.display_name})"
                    )

                except Exception as e:
                    logger.error(
                        f"誕生日クーポン送信エラー: "
                        f"{user.line_user_id} → {e}"
                    )

    finally:
        db.close()


def create_scheduler() -> AsyncIOScheduler:
    """
    スケジューラーの作成と設定
    毎日09:00（日本時間）に誕生日クーポンを配信
    """
    scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")

    scheduler.add_job(
        send_birthday_coupons,
        trigger=CronTrigger(hour=9, minute=0, timezone="Asia/Tokyo"),
        id="birthday_coupons",
        name="誕生日クーポン自動配信",
        replace_existing=True,
        misfire_grace_time=3600,  # 1時間以内の遅延は許容
    )

    return scheduler
