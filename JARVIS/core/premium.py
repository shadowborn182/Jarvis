"""
JARVIS — Per-Guild Premium Subscription Service & Audit Logger
Developer: Shadow
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final

from sqlalchemy import select

from core.cache import AsyncTTLCache
from core.database import DatabaseManager
from database.models import GuildBranding, PremiumAuditLog, PremiumSubscription

logger = logging.getLogger("JARVIS.Premium")


@dataclass(frozen=True)
class PremiumPlan:
    key: str
    display_name: str
    custom_slots: int
    no_prefix: bool
    custom_branding: bool
    custom_banners: bool
    dashboard_pro: bool
    description: str


PREMIUM_PLANS: Final[dict[str, PremiumPlan]] = {
    "starter": PremiumPlan(
        key="starter",
        display_name="JARVIS Starter",
        custom_slots=3,
        no_prefix=True,
        custom_branding=True,
        custom_banners=True,
        dashboard_pro=True,
        description="No Prefix commands, custom embed branding & welcome/goodbye banners.",
    ),
    "pro": PremiumPlan(
        key="pro",
        display_name="JARVIS Pro",
        custom_slots=10,
        no_prefix=True,
        custom_branding=True,
        custom_banners=True,
        dashboard_pro=True,
        description="Full server branding, custom banners, No Prefix & 10 customization slots.",
    ),
    "enterprise": PremiumPlan(
        key="enterprise",
        display_name="JARVIS Enterprise",
        custom_slots=25,
        no_prefix=True,
        custom_branding=True,
        custom_banners=True,
        dashboard_pro=True,
        description="Maximum customization slots, priority dashboard controls & full branding.",
    ),
    "lifetime": PremiumPlan(
        key="lifetime",
        display_name="JARVIS Lifetime",
        custom_slots=50,
        no_prefix=True,
        custom_branding=True,
        custom_banners=True,
        dashboard_pro=True,
        description="Permanent server Premium with all customization features unlocked.",
    ),
}


@dataclass(frozen=True)
class GuildPremiumStatus:
    guild_id: int
    is_premium: bool
    plan_key: str | None
    plan_name: str
    starts_at: datetime | None
    expires_at: datetime | None
    granted_by: int | None
    subscription_id: int | None

    @property
    def is_lifetime(self) -> bool:
        return self.is_premium and self.expires_at is None


class PremiumService:
    """Manages per-guild Premium subscriptions, auto-expiry, caching, and audit logs."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db
        self._cache: AsyncTTLCache[int, GuildPremiumStatus] = AsyncTTLCache(ttl_seconds=60.0)

    @staticmethod
    def normalize_dt(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    async def invalidate(self, guild_id: int) -> None:
        await self._cache.invalidate(guild_id)

    async def get_guild_status(self, guild_id: int, *, bypass_cache: bool = False) -> GuildPremiumStatus:
        """Return active Premium status for a guild, auto-expiring overdue subscriptions."""
        if not bypass_cache:
            cached = await self._cache.get(guild_id)
            if cached is not None:
                # Double-check expiration against wall clock even when cached
                if cached.is_premium and cached.expires_at is not None:
                    if datetime.now(timezone.utc) >= cached.expires_at:
                        await self._cache.invalidate(guild_id)
                    else:
                        return cached
                else:
                    return cached

        now = datetime.now(timezone.utc)
        expired_ids: list[tuple[int, str]] = []

        async with self.db.session() as session:
            result = await session.execute(
                select(PremiumSubscription)
                .where(
                    PremiumSubscription.guild_id == guild_id,
                    PremiumSubscription.active.is_(True),
                )
                .order_by(PremiumSubscription.id.desc())
            )
            subs = list(result.scalars().all())

            active_sub: PremiumSubscription | None = None
            for sub in subs:
                exp = self.normalize_dt(sub.expires_at)
                if exp is not None and now >= exp:
                    sub.active = False
                    expired_ids.append((sub.id, sub.plan_name))
                elif active_sub is None:
                    active_sub = sub

            if expired_ids:
                for sub_id, plan_name in expired_ids:
                    session.add(
                        PremiumAuditLog(
                            guild_id=guild_id,
                            actor_id=0,
                            action="expire",
                            plan_name=plan_name,
                            details=f"Subscription #{sub_id} automatically expired.",
                        )
                    )
                # Disable no-prefix if no active subscription remains
                if active_sub is None:
                    branding_res = await session.execute(
                        select(GuildBranding).where(GuildBranding.guild_id == guild_id)
                    )
                    branding = branding_res.scalar_one_or_none()
                    if branding is not None and branding.no_prefix_enabled:
                        branding.no_prefix_enabled = False

        if active_sub is None:
            status = GuildPremiumStatus(
                guild_id=guild_id,
                is_premium=False,
                plan_key=None,
                plan_name="Free",
                starts_at=None,
                expires_at=None,
                granted_by=None,
                subscription_id=None,
            )
        else:
            plan_obj = PREMIUM_PLANS.get(active_sub.plan_name)
            status = GuildPremiumStatus(
                guild_id=guild_id,
                is_premium=True,
                plan_key=active_sub.plan_name,
                plan_name=plan_obj.display_name if plan_obj else active_sub.plan_name.title(),
                starts_at=self.normalize_dt(active_sub.starts_at),
                expires_at=self.normalize_dt(active_sub.expires_at),
                granted_by=active_sub.granted_by,
                subscription_id=active_sub.id,
            )

        await self._cache.set(guild_id, status)
        return status

    async def grant_premium(
        self,
        guild_id: int,
        actor_id: int,
        plan_name: str = "pro",
        duration: timedelta | None = timedelta(days=30),
        user_id: int | None = None,
        payment_reference: str | None = None,
    ) -> GuildPremiumStatus:
        """Owner-controlled manual Premium grant for a guild."""
        normalized_plan = plan_name.lower().strip()
        if normalized_plan not in PREMIUM_PLANS:
            raise ValueError(f"Unknown plan '{plan_name}'. Valid: {', '.join(PREMIUM_PLANS)}")

        await self.db.ensure_guild(guild_id)
        now = datetime.now(timezone.utc)
        expires_at = None if (normalized_plan == "lifetime" or duration is None) else (now + duration)
        plan_obj = PREMIUM_PLANS[normalized_plan]

        async with self.db.session() as session:
            # Deactivate previous active rows for clean single active record per guild
            prev_res = await session.execute(
                select(PremiumSubscription).where(
                    PremiumSubscription.guild_id == guild_id,
                    PremiumSubscription.active.is_(True),
                )
            )
            for old in prev_res.scalars().all():
                old.active = False

            sub = PremiumSubscription(
                user_id=user_id or actor_id,
                guild_id=guild_id,
                plan_name=normalized_plan,
                server_slots=plan_obj.custom_slots,
                payment_reference=payment_reference,
                active=True,
                expiry_notified=False,
                granted_by=actor_id,
                starts_at=now,
                expires_at=expires_at,
            )
            session.add(sub)
            session.add(
                PremiumAuditLog(
                    guild_id=guild_id,
                    actor_id=actor_id,
                    action="grant",
                    plan_name=normalized_plan,
                    details=(
                        "Granted Lifetime Premium."
                        if expires_at is None
                        else f"Granted until {expires_at.isoformat()}"
                    ),
                )
            )

        await self.invalidate(guild_id)
        return await self.get_guild_status(guild_id, bypass_cache=True)

    async def revoke_premium(self, guild_id: int, actor_id: int, reason: str = "Manual revocation") -> bool:
        """Revoke active Premium for a guild and disable Premium-gated toggles safely."""
        changed = False
        async with self.db.session() as session:
            res = await session.execute(
                select(PremiumSubscription).where(
                    PremiumSubscription.guild_id == guild_id,
                    PremiumSubscription.active.is_(True),
                )
            )
            subs = list(res.scalars().all())
            for sub in subs:
                sub.active = False
                changed = True

            if changed:
                branding_res = await session.execute(
                    select(GuildBranding).where(GuildBranding.guild_id == guild_id)
                )
                branding = branding_res.scalar_one_or_none()
                if branding is not None and branding.no_prefix_enabled:
                    branding.no_prefix_enabled = False

                session.add(
                    PremiumAuditLog(
                        guild_id=guild_id,
                        actor_id=actor_id,
                        action="revoke",
                        plan_name=subs[0].plan_name if subs else "unknown",
                        details=reason,
                    )
                )

        await self.invalidate(guild_id)
        return changed

    async def extend_premium(
        self,
        guild_id: int,
        actor_id: int,
        extra_duration: timedelta,
    ) -> GuildPremiumStatus:
        """Extend an active guild subscription or start a new one if none exists."""
        status = await self.get_guild_status(guild_id, bypass_cache=True)
        if not status.is_premium:
            return await self.grant_premium(
                guild_id=guild_id,
                actor_id=actor_id,
                plan_name="pro",
                duration=extra_duration,
            )

        if status.is_lifetime:
            return status

        now = datetime.now(timezone.utc)
        async with self.db.session() as session:
            res = await session.execute(
                select(PremiumSubscription).where(
                    PremiumSubscription.id == status.subscription_id
                )
            )
            sub = res.scalar_one()
            base_time = max(now, self.normalize_dt(sub.expires_at) or now)
            sub.expires_at = base_time + extra_duration
            sub.expiry_notified = False
            session.add(
                PremiumAuditLog(
                    guild_id=guild_id,
                    actor_id=actor_id,
                    action="extend",
                    plan_name=sub.plan_name,
                    details=f"Extended by {extra_duration}. New expiry: {sub.expires_at.isoformat()}",
                )
            )

        await self.invalidate(guild_id)
        return await self.get_guild_status(guild_id, bypass_cache=True)

    async def activate_from_user_slot(
        self,
        user_id: int,
        guild_id: int,
    ) -> tuple[bool, str]:
        """
        Allow a user who owns an unassigned/available Premium slot (granted by bot owner)
        to bind it to a server where they are an administrator. Never trusts user-provided status.
        """
        now = datetime.now(timezone.utc)
        async with self.db.session() as session:
            # Check if guild already has active premium
            existing_res = await session.execute(
                select(PremiumSubscription).where(
                    PremiumSubscription.guild_id == guild_id,
                    PremiumSubscription.active.is_(True),
                )
            )
            for row in existing_res.scalars().all():
                exp = self.normalize_dt(row.expires_at)
                if exp is None or exp > now:
                    return False, "This server already has an active JARVIS Premium subscription."

            # Look for an unassigned active slot owned by user_id
            slot_res = await session.execute(
                select(PremiumSubscription)
                .where(
                    PremiumSubscription.user_id == user_id,
                    PremiumSubscription.guild_id.is_(None),
                    PremiumSubscription.active.is_(True),
                )
                .order_by(PremiumSubscription.id.asc())
            )
            available_slot = slot_res.scalar_one_or_none()
            if available_slot is None:
                return (
                    False,
                    "No unassigned Premium server slot was found on your account. "
                    "Contact the bot owner (**Shadow**) to obtain a server Premium grant.",
                )

            exp = self.normalize_dt(available_slot.expires_at)
            if exp is not None and exp <= now:
                available_slot.active = False
                return False, "Your unassigned Premium slot has expired."

            await self.db.ensure_guild(guild_id)
            available_slot.guild_id = guild_id
            session.add(
                PremiumAuditLog(
                    guild_id=guild_id,
                    actor_id=user_id,
                    action="activate",
                    plan_name=available_slot.plan_name,
                    details=f"Activated user slot #{available_slot.id} on guild {guild_id}.",
                )
            )

        await self.invalidate(guild_id)
        return True, "JARVIS Premium has been activated for this server."

    async def list_active_subscriptions(self) -> list[PremiumSubscription]:
        """List all currently active non-expired subscriptions."""
        now = datetime.now(timezone.utc)
        active_list: list[PremiumSubscription] = []
        async with self.db.session() as session:
            res = await session.execute(
                select(PremiumSubscription)
                .where(PremiumSubscription.active.is_(True))
                .order_by(PremiumSubscription.id.desc())
            )
            for sub in res.scalars().all():
                exp = self.normalize_dt(sub.expires_at)
                if exp is not None and now >= exp:
                    sub.active = False
                    if sub.guild_id is not None:
                        await self.invalidate(sub.guild_id)
                else:
                    active_list.append(sub)
        return active_list

    async def collect_expiring_and_expired(
        self, warn_before: timedelta = timedelta(hours=24)
    ) -> tuple[list[PremiumSubscription], list[PremiumSubscription]]:
        """
        Process expired subscriptions and return:
        - expiring_soon: active subscriptions expiring within `warn_before` that haven't been notified yet
        - newly_expired: subscriptions that just transitioned to expired
        """
        now = datetime.now(timezone.utc)
        expiring_soon: list[PremiumSubscription] = []
        newly_expired: list[PremiumSubscription] = []

        async with self.db.session() as session:
            res = await session.execute(
                select(PremiumSubscription).where(
                    PremiumSubscription.active.is_(True),
                    PremiumSubscription.expires_at.is_not(None),
                )
            )
            for sub in res.scalars().all():
                exp = self.normalize_dt(sub.expires_at)
                if exp is None:
                    continue
                if now >= exp:
                    sub.active = False
                    newly_expired.append(sub)
                    if sub.guild_id is not None:
                        branding_res = await session.execute(
                            select(GuildBranding).where(GuildBranding.guild_id == sub.guild_id)
                        )
                        branding = branding_res.scalar_one_or_none()
                        if branding is not None and branding.no_prefix_enabled:
                            branding.no_prefix_enabled = False
                        session.add(
                            PremiumAuditLog(
                                guild_id=sub.guild_id,
                                actor_id=0,
                                action="expire",
                                plan_name=sub.plan_name,
                                details=f"Subscription #{sub.id} expired by scheduler.",
                            )
                        )
                        await self.invalidate(sub.guild_id)
                elif (exp - now) <= warn_before and not sub.expiry_notified:
                    sub.expiry_notified = True
                    expiring_soon.append(sub)

        return expiring_soon, newly_expired

    async def get_guild_audit_logs(self, guild_id: int, limit: int = 10) -> list[PremiumAuditLog]:
        async with self.db.session_factory() as session:
            res = await session.execute(
                select(PremiumAuditLog)
                .where(PremiumAuditLog.guild_id == guild_id)
                .order_by(PremiumAuditLog.id.desc())
                .limit(limit)
            )
            return list(res.scalars().all())
