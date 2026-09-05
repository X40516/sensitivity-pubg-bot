"""
Pro Players bilan ishlash. MUHIM: bu modul hech qanday uydirma ma'lumot
yaratmaydi — faqat admin tomonidan kiritilgan yozuvlarni saqlaydi/qaytaradi.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ProPlayer, ProPlayerSensitivity


async def list_players(session: AsyncSession, limit: int = 50) -> list[ProPlayer]:
    result = await session.execute(
        select(ProPlayer).where(ProPlayer.is_active.is_(True)).order_by(ProPlayer.nickname).limit(limit)
    )
    return list(result.scalars().all())


async def top10_players(session: AsyncSession) -> list[ProPlayer]:
    result = await session.execute(
        select(ProPlayer)
        .where(ProPlayer.is_active.is_(True), ProPlayer.rank_position.is_not(None))
        .order_by(ProPlayer.rank_position.asc())
        .limit(10)
    )
    return list(result.scalars().all())


async def get_player(session: AsyncSession, player_id: int) -> ProPlayer | None:
    result = await session.execute(select(ProPlayer).where(ProPlayer.id == player_id))
    return result.scalar_one_or_none()


async def get_player_by_nickname(session: AsyncSession, nickname: str) -> ProPlayer | None:
    result = await session.execute(select(ProPlayer).where(ProPlayer.nickname == nickname))
    return result.scalar_one_or_none()


async def get_latest_sensitivity(session: AsyncSession, player_id: int) -> ProPlayerSensitivity | None:
    result = await session.execute(
        select(ProPlayerSensitivity)
        .where(ProPlayerSensitivity.player_id == player_id)
        .order_by(ProPlayerSensitivity.last_updated.desc())
    )
    return result.scalars().first()


async def filter_players(
    session: AsyncSession,
    region: str | None = None,
    team: str | None = None,
    device: str | None = None,
    fps: int | None = None,
    gyroscope_enabled: bool | None = None,
    play_style: str | None = None,
) -> list[ProPlayer]:
    query = select(ProPlayer).where(ProPlayer.is_active.is_(True))
    if region:
        query = query.where(ProPlayer.region == region)
    if team:
        query = query.where(ProPlayer.team == team)
    if device:
        query = query.where(ProPlayer.device == device)
    if fps:
        query = query.where(ProPlayer.fps == fps)
    if gyroscope_enabled is not None:
        query = query.where(ProPlayer.gyroscope_enabled == gyroscope_enabled)
    if play_style:
        query = query.where(ProPlayer.play_style == play_style)
    result = await session.execute(query.order_by(ProPlayer.nickname))
    return list(result.scalars().all())


async def add_player(
    session: AsyncSession,
    nickname: str,
    team: str | None,
    region: str | None,
    device: str | None,
    fps: int | None,
    gyroscope_enabled: bool | None,
    play_style: str | None,
    source_url: str | None,
    verified: bool,
) -> ProPlayer:
    player = ProPlayer(
        nickname=nickname,
        team=team,
        region=region,
        device=device,
        fps=fps,
        gyroscope_enabled=gyroscope_enabled,
        play_style=play_style,
    )
    session.add(player)
    await session.flush()

    if source_url:
        sensitivity = ProPlayerSensitivity(
            player_id=player.id,
            source_url=source_url,
            verified=verified,
        )
        session.add(sensitivity)

    await session.commit()
    await session.refresh(player)
    return player


async def delete_player(session: AsyncSession, nickname: str) -> bool:
    player = await get_player_by_nickname(session, nickname)
    if not player:
        return False
    await session.delete(player)
    await session.commit()
    return True


async def count_players(session: AsyncSession) -> int:
    result = await session.execute(select(ProPlayer))
    return len(result.scalars().all())
