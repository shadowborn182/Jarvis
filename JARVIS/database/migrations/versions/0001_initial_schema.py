"""Initial JARVIS schema across all 17 modules

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-14 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "guild_settings",
        sa.Column("guild_id", sa.BigInteger(), primary_key=True),
        sa.Column("prefix", sa.String(10), nullable=False, server_default="j!"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("dj_role_id", sa.BigInteger(), nullable=True),
        sa.Column("mod_role_ids", sa.JSON(), nullable=False),
        sa.Column("ignored_channel_ids", sa.JSON(), nullable=False),
        sa.Column("ignored_user_ids", sa.JSON(), nullable=False),
        sa.Column("ignored_commands", sa.JSON(), nullable=False),
        sa.Column("music_24_7", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("music_volume", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "user_settings",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column("timezone_name", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("dm_notifications", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("afk_reason", sa.String(256), nullable=True),
        sa.Column("afk_since", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "security_settings",
        sa.Column("guild_id", sa.BigInteger(), sa.ForeignKey("guild_settings.guild_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("antinuke_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("antiraid_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("antibetray_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("panic_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("night_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("security_level", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("punishment_type", sa.String(20), nullable=False, server_default="quarantine"),
        sa.Column("log_channel_id", sa.BigInteger(), nullable=True),
        sa.Column("quarantine_role_id", sa.BigInteger(), nullable=True),
        sa.Column("jail_role_id", sa.BigInteger(), nullable=True),
        sa.Column("min_account_age_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("raid_join_threshold", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("raid_window_seconds", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("thresholds", sa.JSON(), nullable=False),
        sa.Column("automod_config", sa.JSON(), nullable=False),
        sa.Column("protected_role_ids", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "trusted_whitelists",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("target_type", sa.String(16), nullable=False),
        sa.Column("added_by", sa.BigInteger(), nullable=False),
        sa.Column("note", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("guild_id", "target_id", "target_type", name="uq_whitelist_guild_target"),
    )
    op.create_index("ix_whitelist_guild", "trusted_whitelists", ["guild_id"])


def downgrade() -> None:
    op.drop_index("ix_whitelist_guild", table_name="trusted_whitelists")
    op.drop_table("trusted_whitelists")
    op.drop_table("security_settings")
    op.drop_table("user_settings")
    op.drop_table("guild_settings")
