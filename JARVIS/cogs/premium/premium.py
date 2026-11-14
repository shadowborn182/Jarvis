"""
JARVIS — Premium Subscriptions, Owner Controls, Auto-Expiry & No-Prefix Commands
Developer: Shadow
"""

from __future__ import annotations

import logging
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import BOT_NAME, DEVELOPER_NAME
from core.branding import (
    JarvisColors,
    JarvisEmojis,
    error_embed,
    premium_embed,
    success_embed,
    warning_embed,
)
from core.checks import is_guild_premium, is_jarvis_owner
from core.premium import PREMIUM_PLANS
from core.utilities import parse_duration

logger = logging.getLogger("JARVIS.PremiumCog")


def _command_meta(perms: str = "Everyone", *, is_premium: bool = False, no_prefix: bool = True):
    def decorator(func):
        func.__jarvis_perms__ = perms
        func.__jarvis_premium__ = is_premium
        func.__jarvis_noprefix__ = no_prefix
        return func
    return decorator


class PremiumCog(commands.Cog):
    """Per-guild Premium subscription management, owner grants, and No-Prefix controls."""

    category = "Premium"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.expiration_watcher.start()

    async def cog_unload(self) -> None:
        if self.expiration_watcher.is_running():
            self.expiration_watcher.cancel()

    @tasks.loop(minutes=15)
    async def expiration_watcher(self) -> None:
        """Automatically expire overdue subscriptions and notify server owners before expiry."""
        try:
            expiring_soon, newly_expired = await self.bot.premium.collect_expiring_and_expired(
                warn_before=timedelta(hours=24)
            )
            for sub in expiring_soon:
                if sub.guild_id is None:
                    continue
                guild = self.bot.get_guild(sub.guild_id)
                if guild and guild.owner:
                    try:
                        exp_ts = int(sub.expires_at.timestamp()) if sub.expires_at else 0
                        await guild.owner.send(
                            embed=warning_embed(
                                "JARVIS Premium Expiring Soon",
                                (
                                    f"Premium (`{sub.plan_name.title()}`) for **{guild.name}** "
                                    f"expires <t:{exp_ts}:R>.\n"
                                    f"Contact **{DEVELOPER_NAME}** to renew and retain No Prefix & custom branding."
                                ),
                            )
                        )
                    except discord.HTTPException:
                        pass

            for sub in newly_expired:
                if sub.guild_id is None:
                    continue
                await self.bot.noprefix.invalidate(sub.guild_id)
                guild = self.bot.get_guild(sub.guild_id)
                if guild and guild.owner:
                    try:
                        await guild.owner.send(
                            embed=warning_embed(
                                "JARVIS Premium Expired",
                                (
                                    f"The Premium subscription for **{guild.name}** has expired. "
                                    f"No Prefix has been disabled until Premium is renewed."
                                ),
                            )
                        )
                    except discord.HTTPException:
                        pass
        except Exception as exc:
            logger.exception("Error in Premium expiration_watcher: %s", exc)

    @expiration_watcher.before_loop
    async def before_expiration_watcher(self) -> None:
        await self.bot.wait_until_ready()

    # ==========================================================================
    # PREMIUM COMMAND GROUP
    # ==========================================================================
    @commands.hybrid_group(
        name="premium",
        fallback="status",
        description="Check this server's JARVIS Premium status or manage Premium features.",
    )
    @commands.guild_only()
    @_command_meta("Everyone")
    async def premium_group(self, ctx: commands.Context) -> None:
        await self._send_guild_status(ctx, ctx.guild.id)  # type: ignore[arg-type]

    @premium_group.command(
        name="info",
        description="View JARVIS Premium plans, capabilities, and activation details.",
    )
    @_command_meta("Everyone")
    async def premium_info(self, ctx: commands.Context) -> None:
        embed = premium_embed(
            f"{BOT_NAME} Premium Plans",
            (
                "Upgrade your Discord server with per-server customization and No Prefix commands.\n"
                f"Manual activation is managed securely by **{DEVELOPER_NAME}**."
            ),
        )
        for plan in PREMIUM_PLANS.values():
            embed.add_field(
                name=f"{plan.display_name} (`{plan.key}`)",
                value=(
                    f"{plan.description}\n"
                    f"Slots: `{plan.custom_slots}` · No Prefix: `Yes` · Custom Branding & Banners: `Yes`"
                ),
                inline=False,
            )
        await ctx.reply(embed=embed, mention_author=False)

    @premium_group.command(
        name="features",
        description="List all features unlocked by JARVIS Server Premium.",
    )
    @_command_meta("Everyone")
    async def premium_features(self, ctx: commands.Context) -> None:
        embed = premium_embed(
            f"{BOT_NAME} Premium Features",
            "\n".join(
                [
                    "• **No Prefix Commands** — Run commands like `help`, `ping`, `avatar`, `userinfo` without a prefix.",
                    "• **Custom Embed Branding** — Custom embed colors, title styles, custom footer, footer icon & server logo.",
                    "• **Custom Welcome & Goodbye Banners** — Pillow-rendered banners with custom background, colors & positioning.",
                    "• **Custom Welcome & Goodbye Messages** — Variables `{user}`, `{mention}`, `{server}`, `{member_count}`.",
                    "• **Premium Dashboard Controls** — Live banner previews, color picker & branding management.",
                    "• **Premium Badge & Status** — Highlighted server subscription badge and expiry tracking.",
                ]
            ),
        )
        await ctx.reply(embed=embed, mention_author=False)

    @premium_group.command(
        name="activate",
        description="Activate an owner-assigned Premium slot on this server.",
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @_command_meta("Administrator")
    async def premium_activate(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        ok, msg = await self.bot.premium.activate_from_user_slot(ctx.author.id, ctx.guild.id)
        if ok:
            await ctx.reply(
                embed=success_embed("Premium Activated", msg),
                mention_author=False,
            )
        else:
            await ctx.reply(
                embed=warning_embed("Cannot Activate Premium", msg),
                mention_author=False,
            )

    @premium_group.command(
        name="grant",
        description="Grant JARVIS Premium to a Discord server (Bot Owner only).",
    )
    @is_jarvis_owner()
    @_command_meta("Bot Owner")
    @app_commands.describe(
        guild_id="Target Discord server ID",
        plan="Plan: starter, pro, enterprise, or lifetime",
        duration="Duration like 30d, 90d, 1w, or 'lifetime'",
    )
    async def premium_grant(
        self,
        ctx: commands.Context,
        guild_id: str,
        plan: str = "pro",
        duration: str = "30d",
    ) -> None:
        if not guild_id.isdigit():
            await ctx.reply(embed=error_embed("Invalid Guild ID", "Provide a numeric Discord server ID."), mention_author=False)
            return
        gid = int(guild_id)
        parsed_dur = None if (duration.lower() == "lifetime" or plan.lower() == "lifetime") else parse_duration(duration)
        if duration.lower() != "lifetime" and plan.lower() != "lifetime" and parsed_dur is None:
            await ctx.reply(
                embed=error_embed("Invalid Duration", "Use formats like `30d`, `7d`, `12h`, or `lifetime`."),
                mention_author=False,
            )
            return

        try:
            status = await self.bot.premium.grant_premium(
                guild_id=gid,
                actor_id=ctx.author.id,
                plan_name=plan,
                duration=parsed_dur,
            )
        except ValueError as exc:
            await ctx.reply(embed=error_embed("Invalid Plan", str(exc)), mention_author=False)
            return

        exp_txt = "Lifetime (Never Expires)" if status.expires_at is None else f"<t:{int(status.expires_at.timestamp())}:F>"
        await ctx.reply(
            embed=success_embed(
                "Premium Granted",
                f"**Guild ID:** `{gid}`\n**Plan:** `{status.plan_name}`\n**Expires:** {exp_txt}",
            ),
            mention_author=False,
        )

    @premium_group.command(
        name="revoke",
        description="Revoke JARVIS Premium from a Discord server (Bot Owner only).",
    )
    @is_jarvis_owner()
    @_command_meta("Bot Owner")
    async def premium_revoke(
        self,
        ctx: commands.Context,
        guild_id: str,
        *,
        reason: str = "Revoked by Bot Owner",
    ) -> None:
        if not guild_id.isdigit():
            await ctx.reply(embed=error_embed("Invalid Guild ID", "Provide a numeric Discord server ID."), mention_author=False)
            return
        gid = int(guild_id)
        revoked = await self.bot.premium.revoke_premium(gid, actor_id=ctx.author.id, reason=reason)
        await self.bot.noprefix.invalidate(gid)
        if not revoked:
            await ctx.reply(
                embed=warning_embed("No Active Subscription", f"Guild `{gid}` does not currently have active Premium."),
                mention_author=False,
            )
            return
        await ctx.reply(
            embed=success_embed("Premium Revoked", f"Revoked JARVIS Premium from guild `{gid}`.\nReason: {reason}"),
            mention_author=False,
        )

    @premium_group.command(
        name="extend",
        description="Extend a Discord server's active Premium duration (Bot Owner only).",
    )
    @is_jarvis_owner()
    @_command_meta("Bot Owner")
    async def premium_extend(
        self,
        ctx: commands.Context,
        guild_id: str,
        duration: str = "30d",
    ) -> None:
        if not guild_id.isdigit():
            await ctx.reply(embed=error_embed("Invalid Guild ID", "Provide a numeric Discord server ID."), mention_author=False)
            return
        extra = parse_duration(duration)
        if extra is None:
            await ctx.reply(embed=error_embed("Invalid Duration", "Provide a valid duration like `30d`, `7d`, `1w`."), mention_author=False)
            return

        status = await self.bot.premium.extend_premium(int(guild_id), actor_id=ctx.author.id, extra_duration=extra)
        exp_txt = "Lifetime" if status.expires_at is None else f"<t:{int(status.expires_at.timestamp())}:F>"
        await ctx.reply(
            embed=success_embed(
                "Premium Extended",
                f"**Guild ID:** `{guild_id}`\n**Plan:** `{status.plan_name}`\n**New Expiry:** {exp_txt}",
            ),
            mention_author=False,
        )

    @premium_group.command(
        name="list",
        description="List all active JARVIS Premium servers (Bot Owner only).",
    )
    @is_jarvis_owner()
    @_command_meta("Bot Owner")
    async def premium_list(self, ctx: commands.Context) -> None:
        subs = await self.bot.premium.list_active_subscriptions()
        if not subs:
            await ctx.reply(embed=warning_embed("No Active Subscriptions", "No guilds currently have active Premium."), mention_author=False)
            return
        lines: list[str] = []
        for sub in subs[:20]:
            exp = "Lifetime" if sub.expires_at is None else f"<t:{int(sub.expires_at.timestamp())}:R>"
            guild_obj = self.bot.get_guild(sub.guild_id) if sub.guild_id else None
            g_label = f"{guild_obj.name} (`{sub.guild_id}`)" if guild_obj else f"`{sub.guild_id or 'Unassigned Slot'}`"
            lines.append(f"• {g_label} — `{sub.plan_name}` · Expires: {exp}")
        await ctx.reply(
            embed=premium_embed("Active Premium Subscriptions", "\n".join(lines)),
            mention_author=False,
        )

    @premium_group.command(
        name="check",
        description="Inspect Premium status for any guild ID (Bot Owner only).",
    )
    @is_jarvis_owner()
    @_command_meta("Bot Owner")
    async def premium_check(self, ctx: commands.Context, guild_id: str) -> None:
        if not guild_id.isdigit():
            await ctx.reply(embed=error_embed("Invalid Guild ID", "Provide a numeric Discord server ID."), mention_author=False)
            return
        await self._send_guild_status(ctx, int(guild_id))

    async def _send_guild_status(self, ctx: commands.Context, guild_id: int) -> None:
        status = await self.bot.premium.get_guild_status(guild_id, bypass_cache=True)
        branding = await self.bot.db.get_guild_branding(guild_id)
        guild_obj = self.bot.get_guild(guild_id)
        guild_name = guild_obj.name if guild_obj else f"Guild {guild_id}"

        if not status.is_premium:
            embed = warning_embed(
                f"Premium Status — {guild_name}",
                (
                    f"**Status:** `Inactive (Free Tier)`\n"
                    f"**No Prefix:** `Disabled (Premium Required)`\n\n"
                    f"Run `premium info` to view plans, or ask **{DEVELOPER_NAME}** to grant Premium."
                ),
            )
            await ctx.reply(embed=embed, mention_author=False)
            return

        exp_str = "Lifetime (Never Expires)" if status.expires_at is None else f"<t:{int(status.expires_at.timestamp())}:F> (<t:{int(status.expires_at.timestamp())}:R>)"
        start_str = f"<t:{int(status.starts_at.timestamp())}:F>" if status.starts_at else "N/A"
        embed = premium_embed(
            f"{JarvisEmojis.PREMIUM} Premium Active — {guild_name}",
            f"**Badge:** `JARVIS PREMIUM SERVER`",
        )
        embed.add_field(name="Plan", value=f"`{status.plan_name}`", inline=True)
        embed.add_field(
            name="No Prefix",
            value="`Enabled`" if branding.no_prefix_enabled else "`Disabled`",
            inline=True,
        )
        embed.add_field(name="Embed Color", value=f"`{branding.embed_color}`", inline=True)
        embed.add_field(name="Started", value=start_str, inline=True)
        embed.add_field(name="Expires", value=exp_str, inline=True)
        await ctx.reply(embed=embed, mention_author=False)

    # ==========================================================================
    # NO PREFIX COMMAND GROUP (PREMIUM)
    # ==========================================================================
    @commands.hybrid_group(
        name="noprefix",
        aliases=["np"],
        fallback="status",
        description="Configure JARVIS Premium No-Prefix mode for this server.",
    )
    @commands.guild_only()
    @_command_meta("Manage Server", is_premium=True)
    async def noprefix_group(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        status = await self.bot.premium.get_guild_status(ctx.guild.id)
        branding = await self.bot.db.get_guild_branding(ctx.guild.id)
        state = "Enabled" if (status.is_premium and branding.no_prefix_enabled) else "Disabled"
        embed = await self.bot.make_embed(
            ctx.guild.id,
            title=f"{JarvisEmojis.NOPREFIX} No-Prefix Status",
            description=(
                f"**Server:** {ctx.guild.name}\n"
                f"**Premium:** `{'Active' if status.is_premium else 'Inactive'}`\n"
                f"**No Prefix:** `{state}`\n\n"
                f"When enabled, valid commands like `help`, `ping`, `avatar @user`, `userinfo`, `serverinfo` work without a prefix."
            ),
            color=JarvisColors.BRAND,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @noprefix_group.command(
        name="enable",
        description="Enable No-Prefix commands for this server (Premium + Manage Server).",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def noprefix_enable(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        await self.bot.noprefix.set_enabled_for_guild(ctx.guild.id, True)
        await ctx.reply(
            embed=success_embed(
                "No-Prefix Enabled",
                f"Members in **{ctx.guild.name}** can now execute registered JARVIS commands without a prefix.",
            ),
            mention_author=False,
        )

    @noprefix_group.command(
        name="disable",
        description="Disable No-Prefix commands for this server (Manage Server).",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server", is_premium=True)
    async def noprefix_disable(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        await self.bot.noprefix.set_enabled_for_guild(ctx.guild.id, False)
        await ctx.reply(
            embed=success_embed(
                "No-Prefix Disabled",
                f"No-Prefix mode is now disabled in **{ctx.guild.name}**.",
            ),
            mention_author=False,
        )

    @noprefix_group.command(
        name="toggle",
        description="Toggle No-Prefix mode on or off for this server (Premium + Manage Server).",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def noprefix_toggle(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        current = await self.bot.noprefix.is_enabled_for_guild(ctx.guild.id)
        new_state = not current
        await self.bot.noprefix.set_enabled_for_guild(ctx.guild.id, new_state)
        await ctx.reply(
            embed=success_embed(
                f"No-Prefix {'Enabled' if new_state else 'Disabled'}",
                f"No-Prefix commands are now **{'enabled' if new_state else 'disabled'}** in **{ctx.guild.name}**.",
            ),
            mention_author=False,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PremiumCog(bot))
