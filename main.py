"""
お肉膳スギモト 三井アウトレットパーク岡崎店
LINE公式アカウント Bot サーバー

FastAPI + line-bot-sdk-python v3
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import ApiClient, Configuration
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent,
    UnfollowEvent,
    PostbackEvent,
)

from database import init_db, SessionLocal, get_db
from handlers.follow import handle_follow
from handlers.postback import handle_postback
from handlers.message import handle_message
from scheduler import create_scheduler

# ─────────────────────────────────────────
# 環境変数の読み込み
# ─────────────────────────────────────────
load_dotenv()

CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError(
        "LINE_CHANNEL_SECRET と LINE_CHANNEL_ACCESS_TOKEN を .env に設定してください"
    )

# ─────────────────────────────────────────
# ロギング設定
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# LINE SDK設定
# ─────────────────────────────────────────
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)


# ─────────────────────────────────────────
# アプリライフサイクル
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時
    logger.info("=== お肉膳スギモト LINE Bot 起動 ===")
    init_db()
    logger.info("データベース初期化完了")

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("誕生日クーポンスケジューラー起動（毎日09:00 JST）")

    yield

    # 終了時
    scheduler.shutdown()
    logger.info("=== LINE Bot 停止 ===")


# ─────────────────────────────────────────
# FastAPI アプリ
# ─────────────────────────────────────────
app = FastAPI(
    title="お肉膳スギモト LINE Bot",
    description="三井アウトレットパーク岡崎店 LINE公式アカウント",
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────
# ヘルスチェック
# ─────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "service": "お肉膳スギモト LINE Bot"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ─────────────────────────────────────────
# LINE Webhook エンドポイント
# ─────────────────────────────────────────
@app.post("/callback")
async def callback(request: Request):
    """LINE Webhook受信エンドポイント"""
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    logger.debug(f"Webhook受信: {body_text[:200]}...")

    # 署名検証
    try:
        events = parser.parse(body_text, signature)
    except InvalidSignatureError:
        logger.warning("署名検証失敗")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhookパースエラー: {e}")
        raise HTTPException(status_code=400, detail="Bad request")

    # DBセッション
    db = SessionLocal()

    try:
        with ApiClient(configuration) as api_client:
            for event in events:

                # ──────────────────────
                # 友だち追加
                # ──────────────────────
                if isinstance(event, FollowEvent):
                    logger.info(f"友だち追加: {event.source.user_id}")
                    await handle_follow(event, api_client, db)

                # ──────────────────────
                # ブロック解除（再フォロー扱い）
                # ──────────────────────
                elif isinstance(event, UnfollowEvent):
                    logger.info(f"友だち削除/ブロック: {event.source.user_id}")
                    # フォロー状態をFalseに更新
                    from database import User
                    user = db.query(User).filter(
                        User.line_user_id == event.source.user_id
                    ).first()
                    if user:
                        user.is_following = False
                        db.commit()

                # ──────────────────────
                # リッチメニューボタン押下
                # ──────────────────────
                elif isinstance(event, PostbackEvent):
                    logger.info(f"Postback: {event.source.user_id} → {event.postback.data}")
                    await handle_postback(event, api_client, db)

                # ──────────────────────
                # テキストメッセージ
                # ──────────────────────
                elif isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                    logger.info(f"メッセージ: {event.source.user_id} → {event.message.text[:50]}")
                    await handle_message(event, api_client, db)

    except Exception as e:
        logger.error(f"イベント処理エラー: {e}", exc_info=True)
    finally:
        db.close()

    return JSONResponse(content={"status": "ok"})


# ─────────────────────────────────────────
# 管理用API（テスト・運用補助）
# ─────────────────────────────────────────

@app.post("/admin/broadcast")
async def broadcast(request: Request):
    """
    一斉配信エンドポイント（管理用）

    リクエストボディ例:
    {
        "type": "new_menu",
        "menu_name": "黒毛和牛 特上カルビ",
        "description": "口の中でとろける...",
        "price": "3,300円"
    }
    """
    # ⚠️ 本番環境では必ず認証を追加すること
    data = await request.json()
    msg_type = data.get("type")

    with ApiClient(configuration) as api_client:
        from linebot.v3.messaging import MessagingApi, BroadcastRequest
        from templates.messages import new_menu_broadcast, seasonal_campaign_broadcast

        line_api = MessagingApi(api_client)

        if msg_type == "new_menu":
            messages = [
                new_menu_broadcast(
                    menu_name=data.get("menu_name", "新メニュー"),
                    description=data.get("description", ""),
                    price=data.get("price", "")
                )
            ]
        elif msg_type == "campaign":
            messages = seasonal_campaign_broadcast(
                campaign_title=data.get("title", "キャンペーン"),
                body_text=data.get("body", ""),
                period=data.get("period", "")
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "type は 'new_menu' または 'campaign' を指定してください"}
            )

        line_api.broadcast(BroadcastRequest(messages=messages))

    return JSONResponse(content={"status": "配信完了"})


@app.get("/admin/users/count")
async def user_count():
    """登録ユーザー数確認（管理用）"""
    from database import User
    db = SessionLocal()
    try:
        total = db.query(User).count()
        following = db.query(User).filter(User.is_following == True).count()
        with_birthday = db.query(User).filter(
            User.birthday_month.isnot(None)
        ).count()
        return {
            "total_users": total,
            "following": following,
            "birthday_registered": with_birthday
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("PRODUCTION", "false").lower() != "true",
        log_level="info",
    )
