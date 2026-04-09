"""
ユーザー情報・誕生日管理データベース
SQLite + SQLAlchemy (非同期)
"""
import os
from datetime import date
from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sugimoto.db")

# SQLite の場合は connect_args が必要
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """LINEユーザー情報"""
    __tablename__ = "users"

    line_user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=True)
    # 誕生日（月・日のみ保存 - 年は個人情報保護のため不要）
    birthday_month = Column(Integer, nullable=True)  # 1〜12
    birthday_day = Column(Integer, nullable=True)    # 1〜31
    # フォロー状態
    is_following = Column(Boolean, default=True)
    # セグメント情報（将来のセグメント配信用）
    visit_count = Column(Integer, default=0)         # 来店回数（スタンプ数に連動）
    last_visit_date = Column(Date, nullable=True)
    # 誕生日クーポン送信済みフラグ（年ごとにリセット）
    birthday_coupon_sent_year = Column(Integer, nullable=True)
    # 登録日時
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CouponUsage(Base):
    """クーポン使用履歴"""
    __tablename__ = "coupon_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_user_id = Column(String, index=True)
    coupon_type = Column(String)  # "welcome", "birthday", "stamp_5", "stamp_10", "stamp_20"
    used_at = Column(DateTime, server_default=func.now())


def init_db():
    """テーブル作成"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """DBセッション取得（依存性注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upsert_user(db, line_user_id: str, display_name: str = None):
    """ユーザーの登録または更新"""
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if user is None:
        user = User(line_user_id=line_user_id, display_name=display_name, is_following=True)
        db.add(user)
    else:
        user.is_following = True
        if display_name:
            user.display_name = display_name
    db.commit()
    db.refresh(user)
    return user


def set_birthday(db, line_user_id: str, month: int, day: int):
    """誕生日を登録・更新"""
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if user is None:
        user = User(line_user_id=line_user_id, birthday_month=month, birthday_day=day)
        db.add(user)
    else:
        user.birthday_month = month
        user.birthday_day = day
    db.commit()


def get_birthday_targets(db, month: int, day: int, current_year: int):
    """誕生日が今日でクーポン未送信のユーザー一覧を取得"""
    return db.query(User).filter(
        User.birthday_month == month,
        User.birthday_day == day,
        User.is_following == True,
        (User.birthday_coupon_sent_year != current_year) | (User.birthday_coupon_sent_year.is_(None))
    ).all()


def mark_birthday_coupon_sent(db, line_user_id: str, year: int):
    """誕生日クーポン送信済みにマーク"""
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if user:
        user.birthday_coupon_sent_year = year
        db.commit()


def increment_visit(db, line_user_id: str):
    """来店回数（スタンプ数）を1増やす"""
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if user:
        user.visit_count = (user.visit_count or 0) + 1
        user.last_visit_date = date.today()
        db.commit()
    return user


def get_user_segment(visit_count: int) -> str:
    """
    来店回数からセグメントを判定（将来のセグメント配信用）
    - new: 初来店（1回）
    - regular: 常連（5〜19回）
    - vip: VIP（20回以上）
    - lapsed: 久しぶり（条件は配信時に別途判定）
    """
    if visit_count >= 20:
        return "vip"
    elif visit_count >= 5:
        return "regular"
    elif visit_count >= 1:
        return "new"
    return "prospect"
