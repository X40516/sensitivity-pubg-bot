"""
Saqlangan sensitivity profillari va tarix bilan ishlash.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import SensitivityHistory, SensitivityProfile
from app.services.user_service import is_premium


async def count_profiles(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(select(SensitivityProfile).where(SensitivityProfile.user_id == user_id))
    return len(result.scalars().all())


async def can_save_more(session: AsyncSession, user_id: int) -> bool:
    current = await count_profiles(session, user_id)
    limit = (
        settings.premium_saved_profiles_limit
        if await is_premium(session, user_id)
        else settings.free_saved_profiles_limit
    )
    return current < limit


async def save_profile(
    session: AsyncSession,
    user_id: int,
    name: str,
    result: dict,
) -> SensitivityProfile:
    data = result["input"]
    profile = SensitivityProfile(
        user_id=user_id,
        name=name,
        phone_model=data.get("phone_model"),
        fps=data["fps"],
        gyroscope_enabled=data["gyroscope_enabled"],
        play_style=data["play_style"],
        weapon=data["weapon"],
        scope=data["scope"],
        level=data["level"],
        result_json=result,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def list_profiles(session: AsyncSession, user_id: int) -> list[SensitivityProfile]:
    result = await session.execute(
        select(SensitivityProfile)
        .where(SensitivityProfile.user_id == user_id)
        .order_by(SensitivityProfile.created_at.desc())
    )
    return list(result.scalars().all())


async def get_profile(session: AsyncSession, profile_id: int, user_id: int) -> SensitivityProfile | None:
    result = await session.execute(
        select(SensitivityProfile).where(
            SensitivityProfile.id == profile_id, SensitivityProfile.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def rename_profile(session: AsyncSession, profile_id: int, user_id: int, new_name: str) -> bool:
    profile = await get_profile(session, profile_id, user_id)
    if not profile:
        return False
    profile.name = new_name
    await session.commit()
    return True


async def delete_profile(session: AsyncSession, profile_id: int, user_id: int) -> bool:
    profile = await get_profile(session, profile_id, user_id)
    if not profile:
        return False
    await session.delete(profile)
    await session.commit()
    return True


async def add_history(session: AsyncSession, user_id: int, input_data: dict, result: dict) -> SensitivityHistory:
    history = SensitivityHistory(user_id=user_id, input_json=input_data, result_json=result)
    session.add(history)
    await session.commit()
    return history


async def count_generated(session: AsyncSession) -> int:
    result = await session.execute(select(SensitivityHistory))
    return len(result.scalars().all())
