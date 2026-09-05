"""
Asosiy jadvallar: users, user_settings, sensitivity_profiles, sensitivity_history,
pro_players, pro_player_sensitivities, referrals, premium_users, admin_logs,
translations, bot_settings.
"""
from __future__ import annotations

import datetime as dt
import enum

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class PlayStyle(str, enum.Enum):
    RUSH = "rush"
    SPRAY = "spray"
    BALANCED = "balanced"
    SNIPER = "sniper"


class SensitivityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FPSOption(int, enum.Enum):
    FPS_60 = 60
    FPS_90 = 90
    FPS_120 = 120


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language_code: Mapped[str] = mapped_column(String(8), default="uz")
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    referral_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    referral_bonus_points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    settings: Mapped["UserSettings"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    profiles: Mapped[list["SensitivityProfile"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    history: Mapped[list["SensitivityHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    premium: Mapped["PremiumUser"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    phone_brand: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    default_fps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gyroscope_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    play_style: Mapped[str | None] = mapped_column(String(32), nullable=True)

    user: Mapped["User"] = relationship(back_populates="settings")


class SensitivityProfile(Base):
    """Foydalanuvchi saqlagan sensitivity profillari (masalan: 'My M416')."""

    __tablename__ = "sensitivity_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(64))
    phone_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fps: Mapped[int] = mapped_column(Integer)
    gyroscope_enabled: Mapped[bool] = mapped_column(Boolean)
    play_style: Mapped[str] = mapped_column(String(32))
    weapon: Mapped[str] = mapped_column(String(32))
    scope: Mapped[str] = mapped_column(String(16))
    level: Mapped[str] = mapped_column(String(16))
    result_json: Mapped[dict] = mapped_column(JSON)  # to'liq generatsiya natijasi
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="profiles")


class SensitivityHistory(Base):
    """Har bir generatsiya va AI adjustment tarixi (Premium: sensitivity history)."""

    __tablename__ = "sensitivity_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    input_json: Mapped[dict] = mapped_column(JSON)
    result_json: Mapped[dict] = mapped_column(JSON)
    adjustment_feedback: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="history")


class ProPlayer(Base):
    """Faqat admin tomonidan real, manbali ma'lumot bilan to'ldiriladi. Uydirma yozuv taqiqlanadi."""

    __tablename__ = "pro_players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    team: Mapped[str | None] = mapped_column(String(64), nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gyroscope_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    play_style: Mapped[str | None] = mapped_column(String(32), nullable=True)
    rank_position: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Top-10 uchun, admin belgilaydi
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sensitivities: Mapped[list["ProPlayerSensitivity"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )


class ProPlayerSensitivity(Base):
    """Pro o'yinchining haqiqiy, manba bilan tasdiqlangan (yoki tasdiqlanmagan) sensitivity qiymatlari."""

    __tablename__ = "pro_player_sensitivities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("pro_players.id"))
    camera_sensitivity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ads_sensitivity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    gyroscope_sensitivity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ads_gyroscope_sensitivity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    player: Mapped["ProPlayer"] = relationship(back_populates="sensitivities")


class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (UniqueConstraint("referred_user_id", name="uq_referral_referred_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    referred_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PremiumUser(Base):
    __tablename__ = "premium_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payment_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped["User"] = relationship(back_populates="premium")


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(64))
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Translation(Base):
    """Agar admin runtime tarjima qo'shmoqchi bo'lsa (asosiy tarjimalar JSON fayllarda)."""

    __tablename__ = "translations"
    __table_args__ = (UniqueConstraint("key", "locale", name="uq_translation_key_locale"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    locale: Mapped[str] = mapped_column(String(8))
    value: Mapped[str] = mapped_column(Text)


class BotSetting(Base):
    __tablename__ = "bot_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
