"""
Foydalanuvchi bilan bog'liq database operatsiyalari.
"""
from __future__ import annotations

import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PremiumUser, Referral, User, UserSettings


def _generate_referral_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    username: str | None,
    first_name: str | None,
    referred_by: int | None = None,
) -> User:
    user = await get_user(session, user_id)
    if user:
        user.username = username
        user.first_name = first_name
        await session.commit()
        return user

    referral_code = _generate_referral_code()
    while (await session.execute(select(User).where(User.referral_code == referral_code))).scalar_one_or_none():
        referral_code = _generate_referral_code()

    user = User(
        id=user_id,
        username=username,
        first_name=first_name,
        referral_code=referral_code,
        referred_by=referred_by if referred_by != user_id else None,
    )
    session.add(user)
    await session.flush()

    user.settings = UserSettings(user_id=user_id)
    user.premium = PremiumUser(user_id=user_id, is_active=False)

    if user.referred_by:
        existing_referral = await session.execute(
            select(Referral).where(Referral.referred_user_id == user_id)
        )
        if not existing_referral.scalar_one_or_none():
            session.add(Referral(referrer_id=user.referred_by, referred_user_id=user_id))
            referrer = await get_user(session, user.referred_by)
            if referrer:
                from app.config import settings as app_settings

                referrer.referral_bonus_points += app_settings.referral_bonus_points

    await session.commit()
    await session.refresh(user)
    return user


async def set_language(session: AsyncSession, user_id: int, locale: str) -> None:
    user = await get_user(session, user_id)
    if user:
        user.language_code = locale
        await session.commit()


async def get_user_settings(session: AsyncSession, user_id: int) -> UserSettings | None:
    result = await session.execute(select(UserSettings).where(UserSettings.user_id == user_id))
    return result.scalar_one_or_none()


async def update_phone(session: AsyncSession, user_id: int, brand: str, model: str) -> None:
    settings_row = await get_user_settings(session, user_id)
    if settings_row:
        settings_row.phone_brand = brand
        settings_row.phone_model = model
        await session.commit()


async def is_banned(session: AsyncSession, user_id: int) -> bool:
    user = await get_user(session, user_id)
    return bool(user and user.is_banned)


async def is_premium(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(select(PremiumUser).where(PremiumUser.user_id == user_id))
    premium = result.scalar_one_or_none()
    return bool(premium and premium.is_active)


async def ban_user(session: AsyncSession, user_id: int) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False
    user.is_banned = True
    await session.commit()
    return True


async def unban_user(session: AsyncSession, user_id: int) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False
    user.is_banned = False
    await session.commit()
    return True


async def get_referral_stats(session: AsyncSession, user_id: int) -> tuple[int, int, str]:
    user = await get_user(session, user_id)
    if not user:
        return 0, 0, ""
    result = await session.execute(select(Referral).where(Referral.referrer_id == user_id))
    count = len(result.scalars().all())
    return count, user.referral_bonus_points, user.referral_code


async def get_all_active_user_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(select(User.id).where(User.is_banned.is_(False)))
    return [row[0] for row in result.all()]
