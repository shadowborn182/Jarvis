"""
JARVIS — Complete SQLAlchemy Async ORM Models (SQLite & PostgreSQL Compatible)
Developer: Shadow
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base declarative class for all JARVIS database models."""
    pass


class GuildSettings(Base):
    __tablename__ = "guild_settings"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    prefix: Mapped[str] = mapped_column(String(10), default="j!", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    dj_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mod_role_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    ignored_channel_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    ignored_user_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    ignored_commands: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    music_24_7: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    music_volume: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    security_settings: Mapped[SecuritySettings | None] = relationship(
        back_populates="guild", uselist=False, cascade="all, delete-orphan"
    )
    welcome_settings: Mapped[WelcomeSettings | None] = relationship(
        back_populates="guild", uselist=False, cascade="all, delete-orphan"
    )
    logging_settings: Mapped[LoggingSettings | None] = relationship(
        back_populates="guild", uselist=False, cascade="all, delete-orphan"
    )
    tracker_settings: Mapped[TrackerSettings | None] = relationship(
        back_populates="guild", uselist=False, cascade="all, delete-orphan"
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timezone_name: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    dm_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    afk_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    afk_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class SecuritySettings(Base):
    __tablename__ = "security_settings"

    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True
    )
    antinuke_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    antiraid_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    antibetray_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    panic_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    night_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    security_level: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    punishment_type: Mapped[str] = mapped_column(String(20), default="quarantine", nullable=False)
    log_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    quarantine_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    jail_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    min_account_age_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    raid_join_threshold: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    raid_window_seconds: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    thresholds: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    automod_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    protected_role_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    guild: Mapped[GuildSettings] = relationship(back_populates="security_settings")


class TrustedWhitelist(Base):
    __tablename__ = "trusted_whitelists"
    __table_args__ = (
        UniqueConstraint("guild_id", "target_id", "target_type", name="uq_whitelist_guild_target"),
        Index("ix_whitelist_guild", "guild_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    target_type: Mapped[str] = mapped_column(String(16), nullable=False)  # user, bot, role
    added_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    note: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ModerationCase(Base):
    __tablename__ = "moderation_cases"
    __table_args__ = (
        UniqueConstraint("guild_id", "case_number", name="uq_modcase_guild_number"),
        Index("ix_modcase_guild_user", "guild_id", "target_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    case_number: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="No reason provided", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Warning(Base):
    __tablename__ = "warnings"
    __table_args__ = (Index("ix_warnings_guild_user", "guild_id", "user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class AutoRole(Base):
    __tablename__ = "autoroles"
    __table_args__ = (
        UniqueConstraint("guild_id", "role_id", "target_type", name="uq_autorole_guild_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    target_type: Mapped[str] = mapped_column(String(16), default="all", nullable=False)  # all, human, bot
    delay_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ReactionRole(Base):
    __tablename__ = "reaction_roles"
    __table_args__ = (Index("ix_reaction_roles_msg", "guild_id", "message_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    emoji: Mapped[str | None] = mapped_column(String(128), nullable=True)
    component_type: Mapped[str] = mapped_column(String(20), default="reaction", nullable=False)  # reaction, button, dropdown
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class WelcomeSettings(Base):
    __tablename__ = "welcome_settings"

    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True
    )
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    welcome_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    welcome_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    welcome_embed: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    welcome_image_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    welcome_bg_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    welcome_dm_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    welcome_dm_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    goodbye_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    goodbye_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    goodbye_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    boost_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    boost_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    guild: Mapped[GuildSettings] = relationship(back_populates="welcome_settings")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("guild_id", "ticket_number", name="uq_ticket_guild_number"),
        Index("ix_tickets_guild_status", "guild_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    ticket_number: Mapped[int] = mapped_column(Integer, nullable=False)
    category_name: Mapped[str] = mapped_column(String(64), default="General", nullable=False)
    creator_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    claimed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open, closed, deleted
    close_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    transcript: Mapped[TicketTranscript | None] = relationship(
        back_populates="ticket", uselist=False, cascade="all, delete-orphan"
    )


class TicketTranscript(Base):
    __tablename__ = "ticket_transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tickets.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    ticket: Mapped[Ticket] = relationship(back_populates="transcript")


class Giveaway(Base):
    __tablename__ = "giveaways"
    __table_args__ = (Index("ix_giveaways_active_end", "ended", "ends_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    host_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    prize: Mapped[str] = mapped_column(String(256), nullable=False)
    winner_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    participants: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    winner_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    required_role_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    blacklisted_role_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    min_account_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_server_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class MusicPlaylist(Base):
    __tablename__ = "music_playlists"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_playlist_user_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tracks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class CustomCommand(Base):
    __tablename__ = "custom_commands"
    __table_args__ = (
        UniqueConstraint("guild_id", "trigger", name="uq_custom_cmd_guild_trigger"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    trigger: Mapped[str] = mapped_column(String(64), nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    embed_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class LoggingSettings(Base):
    __tablename__ = "logging_settings"

    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    channels: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    excluded_channel_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    excluded_role_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    enabled_events: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    guild: Mapped[GuildSettings] = relationship(back_populates="logging_settings")


class Birthday(Base):
    __tablename__ = "birthdays"
    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_birthday_guild_user"),
        Index("ix_birthdays_month_day", "birth_month", "birth_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    birth_month: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_day: Mapped[int] = mapped_column(Integer, nullable=False)
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timezone_name: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    last_wished_year: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Marriage(Base):
    __tablename__ = "marriages"
    __table_args__ = (Index("ix_marriages_guild", "guild_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    partner_one_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    partner_two_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    married_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    affection_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CustomRole(Base):
    __tablename__ = "custom_roles"
    __table_args__ = (
        UniqueConstraint("guild_id", "role_id", name="uq_custom_role_guild"),
        Index("ix_custom_roles_owner", "guild_id", "owner_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class PremiumSubscription(Base):
    __tablename__ = "premium_subscriptions"
    __table_args__ = (Index("ix_premium_active_expires", "active", "expires_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    plan_name: Mapped[str] = mapped_column(String(32), default="pro", nullable=False)
    server_slots: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    payment_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserXP(Base):
    __tablename__ = "user_xp"
    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_xp_guild_user"),
        Index("ix_xp_leaderboard", "guild_id", "xp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    voice_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_xp_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bio: Mapped[str | None] = mapped_column(String(300), nullable=True)
    reputation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    badges: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    achievements: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    card_theme: Mapped[str] = mapped_column(String(32), default="obsidian", nullable=False)
    last_daily_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_rep_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (Index("ix_reminders_due", "completed", "remind_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class TrackerSettings(Base):
    __tablename__ = "tracker_settings"

    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True
    )
    join_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    leave_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    boost_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    invite_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    stats_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    track_messages: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    track_voice: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    update_interval_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    guild: Mapped[GuildSettings] = relationship(back_populates="tracker_settings")
