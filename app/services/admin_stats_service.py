"""
Admin statistikasi — barcha raqamlar real database so'rovlaridan olinadi.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PremiumUser, Referral, SensitivityHistory, User


async def get_statistics(session: AsyncSession) -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - dt.timedelta(days=7)
    month_start = now - dt.timedelta(days=30)

    total_users = (await session.execute(select(func.count()).select_from(User))).scalar_one()

    active_users = (
        await session.execute(select(func.count()).select_from(User).where(User.last_active_at >= week_start))
    ).scalar_one()

    daily_users = (
        await session.execute(select(func.count()).select_from(User).where(User.created_at >= today_start))
    ).scalar_one()

    weekly_users = (
        await session.execute(select(func.count()).select_from(User).where(User.created_at >= week_start))
    ).scalar_one()

    monthly_users = (
        await session.execute(select(func.count()).select_from(User).where(User.created_at >= month_start))
    ).scalar_one()

    generated = (await session.execute(select(func.count()).select_from(SensitivityHistory))).scalar_one()

    referrals = (await session.execute(select(func.count()).select_from(Referral))).scalar_one()

    premium = (
        await session.execute(
            select(func.count()).select_from(PremiumUser).where(PremiumUser.is_active.is_(True))
        )
    ).scalar_one()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "daily_users": daily_users,
        "weekly_users": weekly_users,
        "monthly_users": monthly_users,
        "generated": generated,
        "referrals": referrals,
        "premium": premium,
    }
