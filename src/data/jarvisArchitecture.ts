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
  isPremium?: boolean;
  noPrefix?: boolean;
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
    name: 'Phase 1 — Foundation & Premium Upgrade',
    status: 'completed',
    summary:
      'Core AutoShardedBot, Pydantic config, SQLite/PostgreSQL async engine, Alembic migrations (0001 & 0002), No-Prefix engine, Per-Server Premium subscriptions & auto-expiry, Custom Server Branding, Pillow Welcome/Goodbye Banners, FastAPI OAuth2 Dashboard, and upgraded Interactive Help Menu.',
    deliverables: [
      'JARVIS/bot.py + core/ (premium, noprefix, branding, banners, database, errors, permissions, loader)',
      'JARVIS/cogs/premium/premium.py (grant, revoke, extend, activate, list, check, noprefix)',
      'JARVIS/cogs/branding/branding.py + cogs/greetings/greetings.py (Pillow banners & brand commands)',
      'JARVIS/cogs/utility/info.py (avatar, serverinfo, userinfo) + cogs/general/ (help, core_info)',
      'JARVIS/dashboard/ (FastAPI + Discord OAuth2 + CSRF + Live Banner Preview)',
      'JARVIS/tests/test_phase1_foundation.py & test_premium_upgrade.py',
    ],
  },
  {
    id: 2,
    name: 'Phase 2 — Core Features',
    status: 'pending',
    summary: 'Full Utility suite, General XP/Profiles/Rank Cards, Moderation, and Autoroles.',
    deliverables: [
      'Utility cog (reminders, polls, sticky messages, embed builder, custom commands)',
      'General cog (XP leveling, Pillow rank cards, daily rewards, reputation, leaderboards)',
      'Moderation cog (ban, tempban, kick, warn, timeout, purge, channel/voice locks, case history)',
      'Autoroles cog (join/bot/human autoroles, button/dropdown panels)',
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
    summary: 'Lavalink v4 Music system, Customrole, Server Templates, and Marriage.',
    deliverables: [
      'Wavelink Lavalink v4 music player, filters (Bassboost, Nightcore, 8D), 24/7 mode & playlists',
      'Personal Customrole manager with strict dangerous-permission stripping',
      'JSON Template export/restore with destructive confirmation previews',
      'Marriage system & couple leaderboards',
    ],
  },
  {
    id: 6,
    name: 'Phase 6 — Extended Dashboard Modules',
    status: 'completed',
    summary: 'FastAPI backend with Discord OAuth2, CSRF/session security, No-Prefix, Branding, and Welcome/Goodbye Banner Studio.',
    deliverables: [
      'Discord OAuth2 authentication & Manage Server permission gating',
      'Premium status, expiry display, No-Prefix toggle & embed color picker',
      'Live PNG Welcome & Goodbye Banner Preview endpoint & reset controls',
    ],
  },
  {
    id: 7,
    name: 'Phase 7 — Testing & Deployment',
    status: 'pending',
    summary: 'Full automated pytest coverage across remaining modules, security audit, and container hardening.',
    deliverables: [
      'Integration tests for anti-nuke, anti-raid, tickets, and giveaways',
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
    status: 'implemented',
    description: 'Avatar, serverinfo, userinfo active now; reminders, polls & embed builder in Phase 2.',
    keyFeatures: ['avatar / serverinfo / userinfo', 'Reminders & AFK (Phase 2)', 'Sticky messages (Phase 2)'],
  },
  {
    id: 3,
    name: 'General',
    phase: 1,
    status: 'implemented',
    description: 'Interactive 17-category help with Premium/No-Prefix tags, bot stats, uptime & prefix config.',
    keyFeatures: ['Interactive Help Menu', 'Dynamic Server Prefix', 'Bot & Latency Diagnostics'],
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
    phase: 1,
    status: 'implemented',
    description: 'Custom welcome & goodbye Pillow banners, embeds, message variables & event listeners.',
    keyFeatures: ['Pillow PNG banners', 'Welcome & Goodbye channels', 'Test banner command', 'Custom text & positioning'],
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
    phase: 1,
    status: 'implemented',
    description: 'Per-server Premium subscriptions, No-Prefix commands, custom embed branding & auto-expiry.',
    keyFeatures: ['No-Prefix Engine', 'Owner grant/revoke/extend', 'Server Branding & Banners', 'FastAPI Dashboard'],
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
    noPrefix: true,
  },
  {
    name: 'ping',
    category: 'General',
    description: 'Check JARVIS WebSocket gateway and database latency.',
    usage: 'j!ping',
    aliases: [],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'uptime',
    category: 'General',
    description: 'Show how long JARVIS has been running without interruption.',
    usage: 'j!uptime',
    aliases: [],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'botinfo',
    category: 'General',
    description: 'Display JARVIS identity, developer credit, runtime metrics, and server statistics.',
    usage: 'j!botinfo',
    aliases: ['about', 'jarvis'],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'prefix',
    category: 'General',
    description: 'View or update the server prefix for JARVIS prefix commands.',
    usage: 'j!prefix [new_prefix]',
    aliases: [],
    permissions: 'Manage Server',
    noPrefix: true,
  },
  {
    name: 'modules',
    category: 'General',
    description: 'List all 17 JARVIS modules and currently loaded Cog extensions.',
    usage: 'j!modules',
    aliases: [],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'avatar',
    category: 'Utility',
    description: 'Display a member full-resolution avatar.',
    usage: 'j!avatar [member]',
    aliases: ['av', 'pfp'],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'serverinfo',
    category: 'Utility',
    description: 'Display detailed statistics and Premium status for this server.',
    usage: 'j!serverinfo',
    aliases: ['si', 'guildinfo'],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'userinfo',
    category: 'Utility',
    description: 'Display profile details, join date, and roles for a user.',
    usage: 'j!userinfo [member]',
    aliases: ['ui', 'whois'],
    permissions: 'Everyone',
    noPrefix: true,
  },
  {
    name: 'premium',
    category: 'Premium',
    description: 'Check server Premium status, plans, features, or manage grants (Owner).',
    usage: 'j!premium [status|info|features|activate|grant|revoke|extend|list|check]',
    aliases: [],
    permissions: 'Everyone / Bot Owner',
    noPrefix: true,
  },
  {
    name: 'noprefix',
    category: 'Premium',
    description: 'Enable, disable, or toggle Premium No-Prefix commands for this server.',
    usage: 'j!noprefix [status|enable|disable|toggle]',
    aliases: ['np'],
    permissions: 'Manage Server',
    isPremium: true,
    noPrefix: true,
  },
  {
    name: 'brand',
    category: 'Premium',
    description: 'Customize embed color, footer, server logo, welcome/goodbye banners, or preview.',
    usage: 'j!brand [view|color|title|footer|icon|text|welcome|goodbye|preview|reset]',
    aliases: [],
    permissions: 'Manage Server',
    isPremium: true,
    noPrefix: true,
  },
  {
    name: 'welcome',
    category: 'Greetings',
    description: 'Configure welcome channel, toggle, or send a live test banner.',
    usage: 'j!welcome [status|channel|toggle|test]',
    aliases: [],
    permissions: 'Manage Server',
    noPrefix: true,
  },
  {
    name: 'goodbye',
    category: 'Greetings',
    description: 'Configure goodbye channel, toggle, or send a live test banner.',
    usage: 'j!goodbye [status|channel|toggle|test]',
    aliases: [],
    permissions: 'Manage Server',
    noPrefix: true,
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
    table: 'guild_branding',
    model: 'GuildBranding',
    module: 'Premium / Branding / Greetings',
    columns: [
      {name: 'guild_id', type: 'BigInteger (PK, FK)', notes: 'Cascades from guild_settings'},
      {name: 'no_prefix_enabled', type: 'Boolean', notes: 'Premium No-Prefix toggle'},
      {name: 'embed_color', type: 'String(7)', notes: 'Custom hex embed color'},
      {name: 'embed_footer', type: 'String(256)', notes: 'Custom server footer text'},
      {name: 'welcome_banner_bg_url', type: 'String(512)', notes: 'HTTPS custom banner background'},
      {name: 'goodbye_banner_bg_url', type: 'String(512)', notes: 'HTTPS custom goodbye background'},
      {name: 'updated_at', type: 'DateTime(tz)', notes: 'Auto-updated timestamp'},
    ],
  },
  {
    table: 'premium_subscriptions',
    model: 'PremiumSubscription',
    module: 'Premium',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Primary key'},
      {name: 'guild_id', type: 'BigInteger (Index)', notes: 'Target Discord server'},
      {name: 'plan_name', type: 'String(32)', notes: 'starter | pro | enterprise | lifetime'},
      {name: 'active', type: 'Boolean', notes: 'Auto-expired when expires_at passes'},
      {name: 'starts_at', type: 'DateTime(tz)', notes: 'Subscription start timestamp'},
      {name: 'expires_at', type: 'DateTime(tz)', notes: 'Nullable for Lifetime'},
    ],
  },
  {
    table: 'premium_audit_logs',
    model: 'PremiumAuditLog',
    module: 'Premium / Security',
    columns: [
      {name: 'id', type: 'Integer (PK)', notes: 'Primary key'},
      {name: 'guild_id', type: 'BigInteger (Index)', notes: 'Target server'},
      {name: 'actor_id', type: 'BigInteger', notes: 'Owner or system scheduler'},
      {name: 'action', type: 'String(32)', notes: 'grant | revoke | extend | expire | activate'},
      {name: 'plan_name', type: 'String(32)', notes: 'Affected plan'},
    ],
  },
  {
    table: 'welcome_settings',
    model: 'WelcomeSettings',
    module: 'Greetings',
    columns: [
      {name: 'guild_id', type: 'BigInteger (PK, FK)', notes: 'Cascades from guild_settings'},
      {name: 'welcome_enabled', type: 'Boolean', notes: 'Master welcome toggle'},
      {name: 'welcome_channel_id', type: 'BigInteger', notes: 'Destination text channel'},
      {name: 'goodbye_enabled', type: 'Boolean', notes: 'Master goodbye toggle'},
      {name: 'goodbye_channel_id', type: 'BigInteger', notes: 'Destination goodbye channel'},
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
];

export const ALL_23_MODEL_NAMES = [
  'GuildSettings',
  'GuildBranding',
  'PremiumSubscription',
  'PremiumAuditLog',
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
  'UserXP',
  'UserProfile',
  'Reminder',
  'TrackerSettings',
];
