export type PhaseStatus = 'completed' | 'in_progress' | 'pending';

export interface RoadmapPhase {
  id: number;
  name: string;
  status: PhaseStatus;
  summary: string;
  deliverables: string[];
}

export interface ModuleSpec {
  id: number;
  name: string;
  phase: number;
  status: 'implemented' | 'pending';
  description: string;
  keyFeatures: string[];
}

export interface LiveCommandDoc {
  name: string;
  category: string;
  description: string;
  usage: string;
  aliases: string[];
  permissions: string;
}

export interface SchemaModelDoc {
  table: string;
  model: string;
  module: string;
  columns: {name: string; type: string; notes: string}[];
}

export const ROADMAP_PHASES: RoadmapPhase[] = [
  {
    id: 1,
    name: 'Phase 1 — Foundation',
    status: 'completed',
    summary:
      'Core bot runtime, Pydantic configuration, async SQLAlchemy engine, Alembic migrations, dynamic Cog loader, error handler, structured logging, prefix/slash hybrid commands, and interactive 17-category Help menu.',
    deliverables: [
      'JARVIS/bot.py (AutoShardedBot, dynamic prefix cache, presence rotation, graceful shutdown)',
      'JARVIS/config.py (immutable JARVIS / Shadow identity + Pydantic validation)',
      'JARVIS/core/ (database, branding, logger, permissions, checks, errors, utilities, loader, cache, events)',
      'JARVIS/database/models.py (23 ORM models) + Alembic initial migration',
      'JARVIS/cogs/general/ (help.py + core_info.py)',
      'JARVIS/tests/test_phase1_foundation.py + Docker & OS startup scripts',
    ],
  },
  {
    id: 2,
    name: 'Phase 2 — Core Features',
    status: 'pending',
    summary: 'Utility, General (XP/Profiles/Rank Cards), Moderation, Autoroles, and Greetings modules.',
    deliverables: [
      'Utility cog (userinfo, serverinfo, reminders, polls, sticky messages, embed builder)',
      'General cog (XP leveling, Pillow rank cards, daily rewards, reputation, leaderboards)',
      'Moderation cog (ban, tempban, kick, warn, timeout, purge, channel/voice locks, case history)',
      'Autoroles & Greetings cogs (join/bot/human autoroles, button/dropdown panels, welcome banners)',
    ],
  },
  {
    id: 3,
    name: 'Phase 3 — Advanced Security',
    status: 'pending',
    summary: 'Anti-Nuke, Anti-Raid, Anti-Betray, AutoMod, Quarantine, Panic Mode, and Night Mode.',
    deliverables: [
      'Audit log anti-nuke monitor with configurable thresholds & safe permission restoration',
      'Anti-raid join velocity & account age filter with automatic quarantine',
      'AutoMod (anti-scam, anti-phishing, anti-invite, anti-spam, anti-ghost-ping, anti-zalgo)',
    ],
  },
  {
    id: 4,
    name: 'Phase 4 — Community Features',
    status: 'pending',
    summary: 'Fun games, Giveaways, Tickets with HTML transcripts, Tracker, Logging, and Birthdays.',
    deliverables: [
      'Fun cog (Tic-Tac-Toe, Connect Four, RPS, Truth or Dare, Pillow image tools)',
      'Giveaway scheduler with restart-safe buttons & role/age eligibility checks',
      'Ticket panels, claim/close lifecycle & HTML transcript archive',
      'Tracker, granular Logging router & timezone-aware Birthday scheduler',
    ],
  },
  {
    id: 5,
    name: 'Phase 5 — Advanced Features',
    status: 'pending',
    summary: 'Lavalink v4 Music system, Customrole, Server Templates, Marriage, and Premium subscriptions.',
    deliverables: [
      'Wavelink Lavalink v4 music player, filters (Bassboost, Nightcore, 8D), 24/7 mode & playlists',
      'Personal Customrole manager with strict dangerous-permission stripping',
      'JSON Template export/restore with destructive confirmation previews',
      'Marriage system & Premium subscription expiry scheduler',
    ],
  },
  {
    id: 6,
    name: 'Phase 6 — Web Dashboard',
    status: 'pending',
    summary: 'FastAPI backend with Discord OAuth2, CSRF/session security, and full guild configuration UI.',
    deliverables: [
      'Discord OAuth2 authentication & Manage Server permission gating',
      'FastAPI routes for Security, Moderation, Welcome, Autoroles, Tickets, Logging & Music',
      'Responsive dark web frontend with live guild stats & audit history',
    ],
  },
  {
    id: 7,
    name: 'Phase 7 — Testing & Deployment',
    status: 'pending',
    summary: 'Full automated pytest coverage across all modules, security audit, performance tuning, and container hardening.',
    deliverables: [
      'Integration tests for anti-nuke, anti-raid, tickets, giveaways, OAuth2 & premium expiry',
      'Load & rate-limit audit and final Docker Compose verification',
    ],
  },
];

export const MODULE_SPECS: ModuleSpec[] = [
  {
    id: 1,
    name: 'Security',
    phase: 3,
    status: 'pending',
    description: 'Anti-nuke, anti-raid, anti-betray, quarantine, panic & night mode protection.',
    keyFeatures: ['Audit-log anti-nuke', 'Mass-join anti-raid', 'Trusted whitelists', 'Panic & Night mode'],
  },
  {
    id: 2,
    name: 'Utility',
    phase: 2,
    status: 'pending',
    description: 'Server/user info, reminders, polls, sticky messages, embed builder & custom commands.',
    keyFeatures: ['Server & User lookup', 'Reminders & AFK', 'Sticky messages', 'Embed builder'],
  },
  {
    id: 3,
    name: 'General',
    phase: 1,
    status: 'implemented',
    description: 'Interactive 17-category help, bot stats, uptime, prefix config, XP & profiles.',
    keyFeatures: ['Interactive Help Menu', 'Dynamic Server Prefix', 'Bot & Latency Diagnostics', 'XP & Rank Cards (Phase 2)'],
  },
  {
    id: 4,
    name: 'Moderation',
    phase: 2,
    status: 'pending',
    description: 'Ban, tempban, kick, warn, timeout, purge, channel locks & voice moderation.',
    keyFeatures: ['Hierarchy validation', 'Owner protection', 'Case history', 'Timed punishment scheduler'],
  },
  {
    id: 5,
    name: 'Autoroles',
    phase: 2,
    status: 'pending',
    description: 'Join/bot/human autoroles, button roles, dropdown roles & reaction panels.',
    keyFeatures: ['Join/Bot/Human roles', 'Persistent button panels', 'Dropdown selectors', 'Temporary autoroles'],
  },
  {
    id: 6,
    name: 'Fun',
    phase: 4,
    status: 'pending',
    description: 'Mini-games, 8ball, Tic-Tac-Toe, Connect Four, social actions & image tools.',
    keyFeatures: ['Tic-Tac-Toe & Connect 4', 'Truth or Dare', 'Social actions', 'Pillow image effects'],
  },
  {
    id: 7,
    name: 'Greetings',
    phase: 2,
    status: 'pending',
    description: 'Custom welcome/goodbye banners, embeds, DMs & server boost announcements.',
    keyFeatures: ['Custom Pillow banners', 'Message variables', 'Welcome DMs', 'Boost alerts'],
  },
  {
    id: 8,
    name: 'Giveaway',
    phase: 4,
    status: 'pending',
    description: 'Timed multi-winner giveaways with role requirements & restart-safe buttons.',
    keyFeatures: ['Restart-safe entry', 'Role & age filters', 'Multi-winner reroll', 'Giveaway logs'],
  },
  {
    id: 9,
    name: 'Ticket',
    phase: 4,
    status: 'pending',
    description: 'Multi-category support panels, claim/close workflows & HTML transcripts.',
    keyFeatures: ['Multi-category panels', 'Claim & close reasons', 'HTML transcripts', 'Staff feedback'],
  },
  {
    id: 10,
    name: 'Music',
    phase: 5,
    status: 'pending',
    description: 'Lavalink v4 audio playback, queue management, filters, 24/7 mode & playlists.',
    keyFeatures: ['Lavalink v4 / Wavelink', 'Bassboost, Nightcore, 8D', 'Saved user playlists', 'DJ role permissions'],
  },
  {
    id: 11,
    name: 'Tracker',
    phase: 4,
    status: 'pending',
    description: 'Join, leave, boost, invite, message & voice activity analytics.',
    keyFeatures: ['Invite attribution', 'Message & voice stats', 'Auto-updating stat channels', 'Growth tracking'],
  },
  {
    id: 12,
    name: 'Logging',
    phase: 4,
    status: 'pending',
    description: 'Granular audit logs for messages, members, roles, channels, voice & moderation.',
    keyFeatures: ['25+ event types', 'Per-category log channels', 'Channel/role exclusions', 'Actor lookup'],
  },
  {
    id: 13,
    name: 'Birthdays',
    phase: 4,
    status: 'pending',
    description: 'Timezone-aware birthday registration, announcements, roles & upcoming lists.',
    keyFeatures: ['Timezone scheduling', 'Birthday role toggle', 'Upcoming calendar', 'Optional DM wishes'],
  },
  {
    id: 14,
    name: 'Customrole',
    phase: 5,
    status: 'pending',
    description: 'Personal user roles with safe hierarchy & permission boundaries.',
    keyFeatures: ['Dangerous perm stripping', 'Role color & icons', 'Ownership transfer', 'Creation limits'],
  },
  {
    id: 15,
    name: 'Template',
    phase: 5,
    status: 'pending',
    description: 'Server structure, role, embed & configuration JSON backup/restore templates.',
    keyFeatures: ['JSON export/import', 'Restore dry-run preview', 'ConfirmView safeguard', 'Embed templates'],
  },
  {
    id: 16,
    name: 'Marriage',
    phase: 5,
    status: 'pending',
    description: 'Proposals, marriage profiles, anniversaries & couple leaderboards.',
    keyFeatures: ['Interactive proposal view', 'Anniversary tracking', 'Couple leaderboard', 'Shared achievements'],
  },
  {
    id: 17,
    name: 'Premium',
    phase: 5,
    status: 'pending',
    description: 'Subscription plans, server slots, expiry tracking & premium feature access.',
    keyFeatures: ['Server slot allocation', 'Auto-expiry scheduler', 'Verified payment refs', 'Admin management'],
  },
];

export const PHASE1_COMMANDS: LiveCommandDoc[] = [
  {
    name: 'help',
    category: 'General',
    description: 'Open the interactive JARVIS help menu or inspect a specific command.',
    usage: 'j!help [query]',
    aliases: ['h', 'commands'],
    permissions: 'Everyone',
  },
  {
    name: 'ping',
    category: 'General',
    description: 'Check JARVIS WebSocket gateway and database latency.',
    usage: 'j!ping',
    aliases: [],
    permissions: 'Everyone',
  },
  {
    name: 'uptime',
    category: 'General',
    description: 'Show how long JARVIS has been running without interruption.',
    usage: 'j!uptime',
    aliases: [],
    permissions: 'Everyone',
  },
  {
    name: 'botinfo',
    category: 'General',
    description: 'Display JARVIS identity, developer credit, runtime metrics, and server statistics.',
    usage: 'j!botinfo',
    aliases: ['about', 'jarvis'],
    permissions: 'Everyone',
  },
  {
    name: 'prefix',
    category: 'General',
    description: 'View or update the server prefix for JARVIS prefix commands.',
    usage: 'j!prefix [new_prefix]',
    aliases: [],
    permissions: 'Manage Server',
  },
  {
    name: 'modules',
    category: 'General',
    description: 'List all 17 JARVIS modules and currently loaded Cog extensions.',
    usage: 'j!modules',
    aliases: [],
    permissions: 'Everyone',
  },
  {
    name: 'sync',
    category: 'General',
    description: 'Sync JARVIS slash commands to Discord.',
    usage: 'j!sync [scope]',
    aliases: [],
    permissions: 'Bot Owner',
  },
];

export const DATABASE_MODELS: SchemaModelDoc[] = [
  {
    table: 'guild_settings',
    model: 'GuildSettings',
    module: 'Core / Utility / Music',
    columns: [
      {name: 'guild_id', type: 'BigInteger (PK)', notes: 'Discord Guild Snowflake'},
      {name: 'prefix', type: 'String(10)', notes: 'Default: j!'},
      {name: 'mod_role_ids', type: 'JSON', notes: 'Configured moderator role IDs'},
      {name: 'dj_role_id', type: 'BigInteger', notes: 'Optional DJ role for Music'},
      {name: 'music_24_7', type: 'Boolean', notes: 'Persistent 24/7 voice connection'},
    ],
  },
  {
    table: 'security_settings',
    model: 'SecuritySettings',
    module: 'Security',
    columns: [
      {name: 'guild_id', type: 'BigInteger (PK, FK)', notes: 'Cascades from guild_settings'},
      {name: 'antinuke_enabled', type: 'Boolean', notes: 'Master anti-nuke toggle'},
      {name: 'antiraid_enabled', type: 'Boolean', notes: 'Mass-join & age filter'},
      {name: 'panic_mode', type: 'Boolean', notes: 'Emergency server lockdown'},
      {name: 'thresholds', type: 'JSON', notes: 'Action thresholds & window config'},
    ],
  },
  {
    table: 'trusted_whitelists',
    model: 'TrustedWhitelist',
    module: 'Security',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Auto-increment key'},
      {name: 'guild_id', type: 'BigInteger (Index)', notes: 'Target server'},
      {name: 'target_id', type: 'BigInteger', notes: 'Trusted user/bot/role ID'},
      {name: 'target_type', type: 'String(16)', notes: 'user | bot | role'},
    ],
  },
  {
    table: 'moderation_cases',
    model: 'ModerationCase',
    module: 'Moderation',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Internal row ID'},
      {name: 'guild_id', type: 'BigInteger', notes: 'Unique with case_number'},
      {name: 'case_number', type: 'Integer', notes: 'Sequential per-server case'},
      {name: 'action', type: 'String(32)', notes: 'ban, tempban, kick, timeout, etc.'},
      {name: 'expires_at', type: 'DateTime(tz)', notes: 'Used by temporary punishment scheduler'},
    ],
  },
  {
    table: 'warnings',
    model: 'Warning',
    module: 'Moderation',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Warning ID'},
      {name: 'guild_id', type: 'BigInteger', notes: 'Indexed with user_id'},
      {name: 'user_id', type: 'BigInteger', notes: 'Warned member'},
      {name: 'reason', type: 'Text', notes: 'Moderator reason'},
    ],
  },
  {
    table: 'tickets',
    model: 'Ticket',
    module: 'Ticket',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Primary key'},
      {name: 'channel_id', type: 'BigInteger (Unique)', notes: 'Private ticket channel'},
      {name: 'ticket_number', type: 'Integer', notes: 'Sequential per guild'},
      {name: 'status', type: 'String(20)', notes: 'open | closed | deleted'},
      {name: 'claimed_by', type: 'BigInteger', notes: 'Support staff responder'},
    ],
  },
  {
    table: 'ticket_transcripts',
    model: 'TicketTranscript',
    module: 'Ticket',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Primary key'},
      {name: 'ticket_id', type: 'Integer (FK, Unique)', notes: '1:1 with tickets'},
      {name: 'html_content', type: 'Text', notes: 'Archived HTML transcript'},
      {name: 'message_count', type: 'Integer', notes: 'Total archived messages'},
    ],
  },
  {
    table: 'giveaways',
    model: 'Giveaway',
    module: 'Giveaway',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Primary key'},
      {name: 'message_id', type: 'BigInteger (Unique)', notes: 'Persistent giveaway embed'},
      {name: 'prize', type: 'String(256)', notes: 'Reward title'},
      {name: 'ends_at', type: 'DateTime(tz)', notes: 'Indexed for scheduler'},
      {name: 'participants', type: 'JSON', notes: 'Eligible entrant user IDs'},
    ],
  },
  {
    table: 'premium_subscriptions',
    model: 'PremiumSubscription',
    module: 'Premium',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Primary key'},
      {name: 'user_id', type: 'BigInteger', notes: 'Subscriber ID'},
      {name: 'plan_name', type: 'String(32)', notes: 'Tier plan identifier'},
      {name: 'payment_reference', type: 'String(128)', notes: 'Verified external ref'},
      {name: 'expires_at', type: 'DateTime(tz)', notes: 'Indexed auto-expiry timestamp'},
    ],
  },
];

export const ALL_23_MODEL_NAMES = [
  'GuildSettings',
  'UserSettings',
  'SecuritySettings',
  'TrustedWhitelist',
  'ModerationCase',
  'Warning',
  'AutoRole',
  'ReactionRole',
  'WelcomeSettings',
  'Ticket',
  'TicketTranscript',
  'Giveaway',
  'MusicPlaylist',
  'CustomCommand',
  'LoggingSettings',
  'Birthday',
  'Marriage',
  'CustomRole',
  'PremiumSubscription',
  'UserXP',
  'UserProfile',
  'Reminder',
  'TrackerSettings',
];
