"""
JARVIS — Interactive 17-Category Help Menu & Command Search
Dynamically introspects live loaded commands so zero fake commands are ever listed.
Developer: Shadow
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import discord
from discord import app_commands
from discord.ext import commands

from config import BOT_DESCRIPTION, BOT_NAME, DEVELOPER_NAME, OFFICIAL_CATEGORIES
from core.branding import JarvisColors, JarvisEmojis, jarvis_embed, warning_embed
from core.utilities import truncate_text

CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "Security": "Anti-nuke, anti-raid, anti-betray, quarantine, panic & night mode protection.",
    "Utility": "Server/user info, reminders, polls, sticky messages, embed builder & custom commands.",
    "General": "Interactive help, bot stats, XP leveling, profiles, badges & leaderboards.",
    "Moderation": "Ban, tempban, kick, warn, timeout, purge, channel locks & voice moderation.",
    "Autoroles": "Join/bot/human autoroles, button roles, dropdown roles & reaction panels.",
    "Fun": "Mini-games, 8ball, Tic-Tac-Toe, Connect Four, social actions & image tools.",
    "Greetings": "Custom welcome/goodbye banners, embeds, DMs & server boost announcements.",
    "Giveaway": "Timed multi-winner giveaways with role requirements & restart-safe buttons.",
    "Ticket": "Multi-category support panels, claim/close workflows & HTML transcripts.",
    "Music": "Lavalink v4 audio playback, queue management, filters, 24/7 mode & playlists.",
    "Tracker": "Join, leave, boost, invite, message & voice activity analytics.",
    "Logging": "Granular audit logs for messages, members, roles, channels, voice & moderation.",
    "Birthdays": "Timezone-aware birthday registration, announcements, roles & upcoming lists.",
    "Customrole": "Personal user roles with safe hierarchy & permission boundaries.",
    "Template": "Server structure, role, embed & configuration JSON backup/restore templates.",
    "Marriage": "Proposals, marriage profiles, anniversaries & couple leaderboards.",
    "Premium": "Subscription plans, server slots, expiry tracking & premium feature access.",
}

COMMANDS_PER_PAGE = 6


@dataclass(frozen=True)
class CommandDoc:
    name: str
    category: str
    description: str
    usage: str
    aliases: tuple[str, ...]
    permissions: str


def collect_live_commands(bot: commands.Bot, prefix: str = "j!") -> dict[str, list[CommandDoc]]:
    """
    Collect all currently loaded prefix/hybrid commands grouped into the 17 official categories.
    Only real, registered commands are returned.
    """
    grouped: dict[str, list[CommandDoc]] = {cat: [] for cat in OFFICIAL_CATEGORIES}

    for cmd in sorted(bot.commands, key=lambda c: c.qualified_name):
        if cmd.hidden:
            continue

        category = getattr(cmd.cog, "category", "General") if cmd.cog else "General"
        if category not in grouped:
            category = "General"

        # Extract human-readable permission requirement if attached via custom metadata or checks
        perm_label = getattr(cmd, "help_permissions", None) or getattr(
            cmd.callback, "__jarvis_perms__", "Everyone"
        )
        sig = f" {cmd.signature}" if cmd.signature else ""
        usage = f"{prefix}{cmd.qualified_name}{sig}"
        desc = cmd.short_doc or cmd.help or "No description provided."

        grouped[category].append(
            CommandDoc(
                name=cmd.qualified_name,
                category=category,
                description=desc,
                usage=usage,
                aliases=tuple(cmd.aliases),
                permissions=perm_label,
            )
        )

    return grouped


def build_overview_embed(bot: commands.Bot, prefix: str) -> discord.Embed:
    grouped = collect_live_commands(bot, prefix)
    total_commands = sum(len(cmds) for cmds in grouped.values())

    embed = jarvis_embed(
        title=f"{JarvisEmojis.BRAND} {BOT_NAME} Command Matrix",
        description=(
            f"**{BOT_DESCRIPTION}**\n"
            f"Use the dropdown below to inspect any of the **17 modules**, "
            f"navigate pages with **Previous / Next**, or click **Search** to find a command.\n\n"
            f"**Active Prefix:** `{prefix}` · **Slash Commands:** `/help` · "
            f"**Loaded Commands:** `{total_commands}`"
        ),
        color=JarvisColors.BRAND,
    )

    lines: list[str] = []
    for idx, cat in enumerate(OFFICIAL_CATEGORIES, start=1):
        emoji = JarvisEmojis.CATEGORY_MAP.get(cat, "•")
        count = len(grouped[cat])
        status = f"`{count}` cmds" if count > 0 else "`Module Ready / Pending`"
        lines.append(f"`{idx:02d}.` {emoji} **{cat}** — {status}")

    # Split cleanly into two balanced columns
    mid = (len(lines) + 1) // 2
    embed.add_field(name="Modules (1–9)", value="\n".join(lines[:mid]), inline=True)
    embed.add_field(name="Modules (10–17)", value="\n".join(lines[mid:]), inline=True)
    embed.add_field(
        name="Developer & Support",
        value=f"Developed by **{DEVELOPER_NAME}** · Prefix `{prefix}` or `/`",
        inline=False,
    )
    return embed


def build_category_embed(
    bot: commands.Bot,
    category: str,
    prefix: str,
    page: int = 0,
) -> tuple[discord.Embed, int]:
    grouped = collect_live_commands(bot, prefix)
    cmds = grouped.get(category, [])
    emoji = JarvisEmojis.CATEGORY_MAP.get(category, "•")
    cat_desc = CATEGORY_DESCRIPTIONS.get(category, "")

    total_pages = max(1, (len(cmds) + COMMANDS_PER_PAGE - 1) // COMMANDS_PER_PAGE)
    safe_page = max(0, min(page, total_pages - 1))

    embed = jarvis_embed(
        title=f"{emoji} {BOT_NAME} — {category} Module",
        description=cat_desc,
        color=JarvisColors.BRAND,
        footer_note=f"Category: {category} • Page {safe_page + 1}/{total_pages}",
    )

    if not cmds:
        embed.add_field(
            name="No Loaded Commands Yet",
            value=(
                f"The **{category}** module is registered in the JARVIS architecture "
                f"and awaits its phase cog implementation. No placeholder commands are shown."
            ),
            inline=False,
        )
        return embed, total_pages

    start = safe_page * COMMANDS_PER_PAGE
    chunk = cmds[start : start + COMMANDS_PER_PAGE]
    for doc in chunk:
        aliases_txt = ", ".join(f"`{a}`" for a in doc.aliases) if doc.aliases else "None"
        value = (
            f"{doc.description}\n"
            f"**Usage:** `{doc.usage}`\n"
            f"**Aliases:** {aliases_txt} · **Permissions:** `{doc.permissions}`"
        )
        embed.add_field(name=f"`/{doc.name}` / `{prefix}{doc.name}`", value=truncate_text(value), inline=False)

    return embed, total_pages


class CommandSearchModal(discord.ui.Modal, title="Search JARVIS Commands"):
    query_input = discord.ui.TextInput(
        label="Command name or keyword",
        placeholder="e.g. prefix, ping, botinfo, uptime",
        min_length=1,
        max_length=50,
    )

    def __init__(self, view: JarvisHelpView) -> None:
        super().__init__()
        self.help_view = view

    async def on_submit(self, interaction: discord.Interaction) -> None:
        query = self.query_input.value.strip().lower()
        grouped = collect_live_commands(self.help_view.bot, self.help_view.prefix)
        matches: list[CommandDoc] = []
        for cmds in grouped.values():
            for doc in cmds:
                if (
                    query in doc.name.lower()
                    or query in doc.description.lower()
                    or any(query in alias.lower() for alias in doc.aliases)
                ):
                    matches.append(doc)

        if not matches:
            await interaction.response.send_message(
                embed=warning_embed(
                    "No Commands Found",
                    f"No loaded JARVIS command matched `{self.query_input.value}`.",
                ),
                ephemeral=True,
            )
            return

        embed = jarvis_embed(
            title=f"Search Results for '{self.query_input.value}'",
            description=f"Found `{len(matches)}` matching live command(s):",
            color=JarvisColors.INFO,
        )
        for doc in matches[:8]:
            embed.add_field(
                name=f"{JarvisEmojis.CATEGORY_MAP.get(doc.category, '•')} {doc.name} ({doc.category})",
                value=f"{doc.description}\n**Usage:** `{doc.usage}` · **Perms:** `{doc.permissions}`",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class CategorySelect(discord.ui.Select):
    def __init__(self, help_view: JarvisHelpView) -> None:
        self.help_view = help_view
        options = [
            discord.SelectOption(
                label="Overview",
                value="__overview__",
                description="Return to the JARVIS 17-module overview",
                emoji=JarvisEmojis.BRAND,
            )
        ]
        for cat in OFFICIAL_CATEGORIES:
            options.append(
                discord.SelectOption(
                    label=cat,
                    value=cat,
                    description=CATEGORY_DESCRIPTIONS[cat][:95],
                    emoji=JarvisEmojis.CATEGORY_MAP.get(cat),
                )
            )
        super().__init__(
            placeholder="Select a JARVIS module category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="jarvis:help:category_select",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        choice = self.values[0]
        self.help_view.page = 0
        if choice == "__overview__":
            self.help_view.current_category = None
            embed = build_overview_embed(self.help_view.bot, self.help_view.prefix)
            self.help_view.total_pages = 1
        else:
            self.help_view.current_category = choice
            embed, total_pages = build_category_embed(
                self.help_view.bot, choice, self.help_view.prefix, page=0
            )
            self.help_view.total_pages = total_pages
        self.help_view.sync_button_states()
        await interaction.response.edit_message(embed=embed, view=self.help_view)


class JarvisHelpView(discord.ui.View):
    """Persistent-capable interactive help navigation view for JARVIS."""

    def __init__(
        self,
        bot: commands.Bot,
        prefix: str = "j!",
        author_id: int | None = None,
        timeout: float | None = 180.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.bot = bot
        self.prefix = prefix
        self.author_id = author_id
        self.current_category: str | None = None
        self.page: int = 0
        self.total_pages: int = 1
        self.message: discord.Message | None = None

        self.add_item(CategorySelect(self))
        self.sync_button_states()

    def sync_button_states(self) -> None:
        in_category = self.current_category is not None
        self.prev_button.disabled = (not in_category) or self.page <= 0
        self.next_button.disabled = (not in_category) or self.page >= (self.total_pages - 1)
        self.home_button.disabled = not in_category

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.author_id is not None and interaction.user.id != self.author_id:
            await interaction.response.send_message(
                embed=warning_embed(
                    "Interactive Help",
                    "Run `/help` yourself to open your own interactive JARVIS menu.",
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True  # type: ignore[attr-defined]
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(
        label="Previous",
        style=discord.ButtonStyle.secondary,
        custom_id="jarvis:help:prev",
        row=1,
    )
    async def prev_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        if self.current_category is None:
            return
        self.page = max(0, self.page - 1)
        embed, self.total_pages = build_category_embed(
            self.bot, self.current_category, self.prefix, page=self.page
        )
        self.sync_button_states()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Home",
        style=discord.ButtonStyle.primary,
        custom_id="jarvis:help:home",
        row=1,
    )
    async def home_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        self.current_category = None
        self.page = 0
        self.total_pages = 1
        self.sync_button_states()
        embed = build_overview_embed(self.bot, self.prefix)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Next",
        style=discord.ButtonStyle.secondary,
        custom_id="jarvis:help:next",
        row=1,
    )
    async def next_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        if self.current_category is None:
            return
        self.page = min(self.total_pages - 1, self.page + 1)
        embed, self.total_pages = build_category_embed(
            self.bot, self.current_category, self.prefix, page=self.page
        )
        self.sync_button_states()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Search",
        style=discord.ButtonStyle.success,
        custom_id="jarvis:help:search",
        row=1,
    )
    async def search_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        await interaction.response.send_modal(CommandSearchModal(self))


class HelpCog(commands.Cog):
    """JARVIS Interactive Help Command & Category Explorer."""

    category = "General"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        aliases=["h", "commands"],
        description="Open the interactive JARVIS help menu or inspect a specific command.",
    )
    @app_commands.describe(query="Optional command name or category to look up")
    async def help_command(self, ctx: commands.Context, *, query: str | None = None) -> None:
        prefix = ctx.clean_prefix or getattr(self.bot.settings, "default_prefix", "j!")

        if query:
            cleaned = query.strip()
            # Match category directly (case-insensitive)
            matched_cat = next(
                (cat for cat in OFFICIAL_CATEGORIES if cat.lower() == cleaned.lower()),
                None,
            )
            if matched_cat:
                view = JarvisHelpView(self.bot, prefix=prefix, author_id=ctx.author.id)
                view.current_category = matched_cat
                embed, view.total_pages = build_category_embed(self.bot, matched_cat, prefix, page=0)
                view.sync_button_states()
                msg = await ctx.reply(embed=embed, view=view, mention_author=False)
                view.message = msg
                return

            # Match exact command
            cmd = self.bot.get_command(cleaned.lower())
            if cmd and not cmd.hidden:
                cat = getattr(cmd.cog, "category", "General") if cmd.cog else "General"
                sig = f" {cmd.signature}" if cmd.signature else ""
                aliases = ", ".join(f"`{a}`" for a in cmd.aliases) if cmd.aliases else "None"
                perms = getattr(cmd.callback, "__jarvis_perms__", "Everyone")
                embed = jarvis_embed(
                    title=f"{JarvisEmojis.CATEGORY_MAP.get(cat, '•')} Command: {cmd.qualified_name}",
                    description=cmd.help or cmd.short_doc or "No description provided.",
                    color=JarvisColors.INFO,
                )
                embed.add_field(name="Category", value=cat, inline=True)
                embed.add_field(name="Permissions", value=f"`{perms}`", inline=True)
                embed.add_field(name="Aliases", value=aliases, inline=True)
                embed.add_field(
                    name="Usage",
                    value=f"`{prefix}{cmd.qualified_name}{sig}`\n`/{cmd.qualified_name}{sig}`",
                    inline=False,
                )
                await ctx.reply(embed=embed, mention_author=False)
                return

            await ctx.reply(
                embed=warning_embed(
                    "Command Not Found",
                    f"No live command or module matched `{cleaned}`. Run `{prefix}help` to browse all modules.",
                ),
                mention_author=False,
            )
            return

        view = JarvisHelpView(self.bot, prefix=prefix, author_id=ctx.author.id)
        embed = build_overview_embed(self.bot, prefix)
        msg = await ctx.reply(embed=embed, view=view, mention_author=False)
        view.message = msg


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
