"""Add per-guild branding, no-prefix, premium audit logs & expiry tracking

Revision ID: 0002_premium_branding_noprefix
Revises: 0001_initial_schema
Create Date: 2026-11-14 04:40:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_premium_branding_noprefix"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return name in inspector.get_table_names()


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return any(col["name"] == column for col in inspector.get_columns(table))


def upgrade() -> None:
    if not _table_exists("welcome_settings"):
        op.create_table(
            "welcome_settings",
            sa.Column(
                "guild_id",
                sa.BigInteger(),
                sa.ForeignKey("guild_settings.guild_id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("welcome_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("welcome_channel_id", sa.BigInteger(), nullable=True),
            sa.Column("welcome_message", sa.Text(), nullable=True),
            sa.Column("welcome_embed", sa.JSON(), nullable=True),
            sa.Column("welcome_image_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("welcome_bg_url", sa.String(512), nullable=True),
            sa.Column("welcome_dm_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("welcome_dm_message", sa.Text(), nullable=True),
            sa.Column("goodbye_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("goodbye_channel_id", sa.BigInteger(), nullable=True),
            sa.Column("goodbye_message", sa.Text(), nullable=True),
            sa.Column("boost_channel_id", sa.BigInteger(), nullable=True),
            sa.Column("boost_message", sa.Text(), nullable=True),
        )

    if not _table_exists("premium_subscriptions"):
        op.create_table(
            "premium_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.BigInteger(), nullable=False),
            sa.Column("guild_id", sa.BigInteger(), nullable=True),
            sa.Column("plan_name", sa.String(32), nullable=False, server_default="pro"),
            sa.Column("server_slots", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("payment_reference", sa.String(128), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("expiry_notified", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("granted_by", sa.BigInteger(), nullable=True),
            sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_premium_active_expires", "premium_subscriptions", ["active", "expires_at"])
        op.create_index("ix_premium_guild_active", "premium_subscriptions", ["guild_id", "active"])
    else:
        if not _column_exists("premium_subscriptions", "expiry_notified"):
            op.add_column(
                "premium_subscriptions",
                sa.Column("expiry_notified", sa.Boolean(), nullable=False, server_default=sa.false()),
            )
        if not _column_exists("premium_subscriptions", "granted_by"):
            op.add_column(
                "premium_subscriptions",
                sa.Column("granted_by", sa.BigInteger(), nullable=True),
            )
        if not _column_exists("premium_subscriptions", "updated_at"):
            op.add_column(
                "premium_subscriptions",
                sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            )

    if not _table_exists("guild_branding"):
        op.create_table(
            "guild_branding",
            sa.Column(
                "guild_id",
                sa.BigInteger(),
                sa.ForeignKey("guild_settings.guild_id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("no_prefix_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("embed_color", sa.String(7), nullable=False, server_default="#38BDF8"),
            sa.Column("embed_title_style", sa.String(24), nullable=False, server_default="default"),
            sa.Column("embed_footer", sa.String(256), nullable=True),
            sa.Column("footer_icon_url", sa.String(512), nullable=True),
            sa.Column("server_logo_url", sa.String(512), nullable=True),
            sa.Column("branding_text", sa.String(256), nullable=True),
            sa.Column("welcome_banner_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("welcome_banner_bg_url", sa.String(512), nullable=True),
            sa.Column("welcome_banner_text", sa.String(256), nullable=True),
            sa.Column("welcome_banner_text_color", sa.String(7), nullable=False, server_default="#F8FAFC"),
            sa.Column("welcome_banner_accent_color", sa.String(7), nullable=False, server_default="#38BDF8"),
            sa.Column("welcome_banner_text_position", sa.String(16), nullable=False, server_default="center"),
            sa.Column("goodbye_banner_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("goodbye_banner_bg_url", sa.String(512), nullable=True),
            sa.Column("goodbye_banner_text", sa.String(256), nullable=True),
            sa.Column("goodbye_banner_text_color", sa.String(7), nullable=False, server_default="#F8FAFC"),
            sa.Column("goodbye_banner_accent_color", sa.String(7), nullable=False, server_default="#F59E0B"),
            sa.Column("goodbye_banner_text_position", sa.String(16), nullable=False, server_default="center"),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )

    if not _table_exists("premium_audit_logs"):
        op.create_table(
            "premium_audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("guild_id", sa.BigInteger(), nullable=False),
            sa.Column("actor_id", sa.BigInteger(), nullable=False),
            sa.Column("action", sa.String(32), nullable=False),
            sa.Column("plan_name", sa.String(32), nullable=False),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_premium_audit_guild", "premium_audit_logs", ["guild_id", "created_at"])


def downgrade() -> None:
    if _table_exists("premium_audit_logs"):
        op.drop_index("ix_premium_audit_guild", table_name="premium_audit_logs")
        op.drop_table("premium_audit_logs")
    if _table_exists("guild_branding"):
        op.drop_table("guild_branding")
