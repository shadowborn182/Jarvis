# JARVIS — Advanced All-In-One Discord Management Bot

**Bot Name:** JARVIS  
**Developer:** Shadow  
**Language:** Python 3.12+ (3.13 compatible)  
**Discord Library:** `discord.py 2.x`  
**Database:** SQLite (`aiosqlite` for local development) & PostgreSQL (`asyncpg` for production) via SQLAlchemy 2.0 Async + Alembic  
**Music Engine:** Lavalink v4 (`wavelink`)  
**Web Dashboard:** FastAPI + Discord OAuth2  

---

## Table of Contents
1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Current Features & 17-Module Roadmap](#2-current-features--17-module-roadmap)
3. [Discord Developer Portal Setup (Step-by-Step)](#3-discord-developer-portal-setup-step-by-step)
4. [Environment Configuration (`.env`)](#4-environment-configuration-env)
5. [How to Run the Bot](#5-how-to-run-the-bot)
   - [Windows Command Prompt (CMD)](#windows-command-prompt-cmd)
   - [Windows PowerShell](#windows-powershell)
   - [Linux / Linux Mint](#linux--linux-mint)
   - [Docker Compose (Production Stack)](#docker-compose-production-stack)
6. [How to Use JARVIS (Commands & Interactive Help)](#6-how-to-use-jarvis-commands--interactive-help)
7. [Database Migrations & Backups](#7-database-migrations--backups)
8. [Running Automated Tests](#8-running-automated-tests)
9. [Project Folder Structure](#9-project-folder-structure)
10. [Troubleshooting Guide](#10-troubleshooting-guide)

---

## 1. Project Overview & Architecture

JARVIS is a modular, production-structured Discord management bot written **100% in Python** using `discord.py 2.x`, asynchronous database operations, structured rotating file logging, and isolated Cog extensions.

Key architectural principles:
- **Modular Cogs:** Features live in isolated modules under `cogs/<category>/` and are auto-discovered by `core/loader.py`.
- **Dual Command Support:** Hybrid commands work seamlessly as both **prefix commands** (default `j!`, configurable per server) and **Discord slash commands** (`/`).
- **Database Persistence:** All guild settings, prefixes, security rules, moderation cases, tickets, giveaways, XP, birthdays, and subscriptions are modeled in `database/models.py` (23 normalized tables) and managed with Alembic migrations.
- **Role Hierarchy & Safety:** `core/permissions.py` enforces server-owner protection, role hierarchy checks, bot permission checks, and strips dangerous flags (`administrator`, `manage_roles`, etc.) from user-created roles.
- **Global Error Handling:** `core/errors.py` handles permission errors, cooldowns, invalid arguments, database errors, rate limits, and API timeouts cleanly with branded JARVIS embeds.

---

## 2. Current Features & 17-Module Roadmap

### Currently Implemented & Active (Phase 1 — Foundation)
- **Bot Core & Lifecycle (`bot.py`, `core/events.py`):**
  - `AutoShardedBot` startup with automatic guild provisioning on `on_guild_join`.
  - Dynamic per-server prefix resolution backed by `AsyncTTLCache` and database persistence.
  - Rotating bot presence (`JARVIS | /help`, `Protecting {servers} Servers`, `Developed by Shadow`).
  - Graceful `SIGINT` / `SIGTERM` shutdown and clean database connection disposal.
- **Interactive 17-Category Help Menu (`cogs/general/help.py`):**
  - Dark-themed branded embed with dropdown category selector, `Previous` / `Home` / `Next` pagination buttons, and an interactive **Command Search** modal.
  - Dynamically introspects live loaded commands so only real, working commands are shown.
- **Core Diagnostic & Management Commands (`cogs/general/core_info.py`):**
  - `ping` — Checks WebSocket gateway latency and live database query latency.
  - `uptime` — Displays continuous bot uptime and exact start timestamp.
  - `botinfo` — Displays JARVIS identity, developer credit (**Shadow**), Python/`discord.py` versions, server count, member count, memory usage, and command count.
  - `prefix` — View or update the server's custom command prefix (persisted in DB).
  - `modules` — Lists all 17 architecture modules and currently loaded Cog extensions.
  - `sync` — Owner-only slash command tree synchronization (`global` or `guild`).
- **Database Schema & Migrations (`database/models.py`, `database/migrations/`):**
  - Complete 23-table SQLAlchemy 2.0 Async ORM schema ready for all 17 modules, plus SQLite WAL mode, PostgreSQL pooling, health checks, and SQLite backup utilities.

### 17 Official Modules (Full Roadmap)
| # | Module | Phase | Capabilities |
|---|---|---|---|
| 01 | **Security** | Phase 3 | Anti-nuke (channel/role/ban/kick/webhook/escalation), anti-raid, anti-betray, quarantine, jail, panic mode, night mode, automod |
| 02 | **Utility** | Phase 2 | Server/user/role/channel/invite info, avatar, banner, AFK, reminders, calculator, polls, embed builder, sticky messages, custom commands |
| 03 | **General** | Phase 1 & 2 | Interactive help (Active), bot stats (Active), XP & leveling, Pillow rank cards, daily rewards, reputation, badges, leaderboards |
| 04 | **Moderation** | Phase 2 | Ban, tempban, softban, kick, warn, timeout, purge, slowmode, channel/category lock & hide, voice mod, case history |
| 05 | **Autoroles** | Phase 2 | Join/bot/human autoroles, temporary autoroles, button roles, dropdown roles, reaction role panels |
| 06 | **Fun** | Phase 4 | 8ball, coin flip, dice, RPS, Tic-Tac-Toe, Connect Four, Truth or Dare, Would You Rather, ship, social actions, image tools |
| 07 | **Greetings** | Phase 2 | Welcome & goodbye embeds, custom Pillow welcome banners, DMs, boost announcements, message variables |
| 08 | **Giveaway** | Phase 4 | Timed multi-winner giveaways, reroll, required/blacklisted roles, account/server age checks, restart-safe buttons |
| 09 | **Ticket** | Phase 4 | Multi-category button/dropdown panels, claim/close/reopen/delete, member management, HTML transcripts, feedback ratings |
| 10 | **Music** | Phase 5 | Lavalink v4 (`wavelink`) playback, queue, loop, shuffle, seek, volume, filters (Bassboost, Nightcore, 8D, Karaoke), 24/7 mode, playlists |
| 11 | **Tracker** | Phase 4 | Join, leave, boost, invite, message, and voice activity tracking + auto-updating stat channels |
| 12 | **Logging** | Phase 4 | 25+ audit events across separate log channels with actor lookup and channel/role exclusions |
| 13 | **Birthdays** | Phase 4 | Timezone-aware birthday registration, announcements, birthday role, upcoming list, optional DMs |
| 14 | **Customrole** | Phase 5 | Personal user roles with color/icon customization, ownership transfer, and strict dangerous-permission protection |
| 15 | **Template** | Phase 5 | Server structure, role, permission, embed, and config JSON export/import with restore preview & confirmation |
| 16 | **Marriage** | Phase 5 | Interactive marriage proposals, marriage profiles, anniversaries, affection points, couple leaderboard |
| 17 | **Premium** | Phase 5 | Subscription plans, server slots, automatic expiry, admin management, verified payment references |

*Plus **Phase 6 (FastAPI Web Dashboard with Discord OAuth2)** and **Phase 7 (Full Integration Testing & Hardening)**.*

---

## 3. Discord Developer Portal Setup (Step-by-Step)

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**.
2. Name the application **JARVIS** and save.
3. Open the **Bot** tab on the left:
   - Click **Reset Token** (or **View Token**) and copy your bot token. **Never share or commit this token.**
   - Scroll down to **Privileged Gateway Intents** and enable **all three**:
     - **Presence Intent**
     - **Server Members Intent**
     - **Message Content Intent**
   - Click **Save Changes**.
4. Open **OAuth2 -> General**:
   - Copy your **Client ID** and **Client Secret** (needed for `.env` and the FastAPI dashboard).
   - Under **Redirects**, add `http://localhost:8080/auth/callback` (or your production dashboard URL).
5. Open **OAuth2 -> URL Generator**:
   - Under **Scopes**, check `bot` and `applications.commands`.
   - Under **Bot Permissions**, select `Administrator` (recommended for full moderation/security/channel management) or the specific permissions required for your server.
   - Open the generated invite URL in your browser to add **JARVIS** to your Discord server.

---

## 4. Environment Configuration (`.env`)

Inside `JARVIS/`, copy `.env.example` to `.env` and fill in your credentials:

```env
# Discord Bot Credentials
DISCORD_TOKEN="PASTE_YOUR_BOT_TOKEN_HERE"
DISCORD_CLIENT_ID="PASTE_YOUR_CLIENT_ID_HERE"
DISCORD_CLIENT_SECRET="PASTE_YOUR_CLIENT_SECRET_HERE"
BOT_OWNER_IDS="YOUR_DISCORD_USER_ID"

# Bot Behavior
DEFAULT_PREFIX="j!"
ENVIRONMENT="development"
LOG_LEVEL="INFO"

# Database (SQLite local default — switch to postgresql+asyncpg://... for production)
DATABASE_URL="sqlite+aiosqlite:///./database/jarvis.db"
```

> **Tip:** To get your `BOT_OWNER_IDS`, enable **Developer Mode** in Discord (`Settings -> Advanced -> Developer Mode`), right-click your username, and click **Copy User ID**.

---

## 5. How to Run the Bot

### Windows Command Prompt (CMD)
```bat
cd JARVIS
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
alembic upgrade head
python bot.py
```
*Shortcut:* Double-click or run `scripts\start.bat`.

### Windows PowerShell
```powershell
cd JARVIS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
alembic upgrade head
python bot.py
```
*Shortcut:* Run `.\scripts\start.ps1`. (If PowerShell blocks script execution, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.)

### Linux / Linux Mint
```bash
cd JARVIS
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
alembic upgrade head
python bot.py
```
*Shortcut:*
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### Docker Compose (Production Stack)
Launches **JARVIS Bot**, **PostgreSQL 16**, **Lavalink v4**, and **FastAPI Dashboard** together:
```bash
cd JARVIS
cp .env.example .env
# Edit .env with your DISCORD_TOKEN, Client ID/Secret, and strong SESSION_SECRET / CSRF_SECRET
docker compose up -d --build
docker compose logs -f jarvis-bot
```

---

## 6. How to Use JARVIS (Commands & Interactive Help)

### Step 1: Sync Slash Commands (First Run)
After inviting JARVIS and starting `bot.py`, run the prefix command as the configured Bot Owner inside a server:
```text
j!sync
```
Or sync instantly to your current test server only:
```text
j!sync guild
```
Once synced, Discord `/` slash commands appear immediately.

### Step 2: Open the Interactive Help Menu
Run either:
- Prefix: `j!help` (aliases: `j!h`, `j!commands`)
- Slash: `/help`
- Look up a specific command or category: `j!help prefix` or `j!help General`

Inside the Help Menu:
- Use the **Module Dropdown** to jump between all 17 categories.
- Use **Previous**, **Home**, and **Next** buttons to paginate commands.
- Click **Search** to open a modal and filter live commands by name, keyword, or alias.

### Step 3: Live Phase 1 Commands Reference
| Command | Slash | Prefix Example | Description | Required Permission |
|---|---|---|---|---|
| `help` | `/help [query]` | `j!help`, `j!help ping` | Opens interactive help or inspects a command/category | Everyone |
| `ping` | `/ping` | `j!ping` | Shows Discord Gateway ping & database query latency | Everyone |
| `uptime` | `/uptime` | `j!uptime` | Shows how long JARVIS has been online | Everyone |
| `botinfo` | `/botinfo` | `j!botinfo` (aliases: `about`, `jarvis`) | Shows developer credit, Python/`discord.py` versions, servers, members & RAM | Everyone |
| `prefix` | `/prefix [new_prefix]` | `j!prefix`, `j!prefix !` | Views or changes the server command prefix (persisted in DB) | Manage Server |
| `modules` | `/modules` | `j!modules` | Lists all 17 modules and currently loaded Python extensions | Everyone |
| `sync` | *Prefix only* | `j!sync`, `j!sync guild` | Syncs slash commands with Discord | Bot Owner (`BOT_OWNER_IDS`) |

---

## 7. Database Migrations & Backups

- **Apply latest migrations:**
  ```bash
  alembic upgrade head
  ```
- **Create a new migration after editing `database/models.py`:**
  ```bash
  alembic revision --autogenerate -m "describe_change"
  alembic upgrade head
  ```
- **Switch to PostgreSQL in Production:**
  Update `DATABASE_URL` in `.env` to:
  ```env
  DATABASE_URL="postgresql+asyncpg://jarvis_user:your_password@localhost:5432/jarvis"
  ```
- **Local SQLite Backups:** `DatabaseManager.backup_sqlite()` creates timestamped copies in `database/backups/`.

---

## 8. Running Automated Tests

Install dependencies inside your virtual environment, then run:
```bash
cd JARVIS
pytest -v
```
`tests/test_phase1_foundation.py` verifies:
- Permanent JARVIS & Shadow identity constants and 17-category registry
- Prefix validation rules in `Settings`
- Duration parser & formatter (`10m`, `2h 30m`, `1w`)
- Role hierarchy & server-owner protection (`can_moderate_target`)
- Dangerous permission detection & stripping
- Async TTL cache & SQLite async guild prefix persistence

---

## 9. Project Folder Structure

```text
JARVIS/
├── bot.py                        # Main AutoShardedBot entrypoint & lifecycle
├── config.py                     # Permanent identity + Pydantic Settings
├── requirements.txt              # Python 3.12+ dependencies
├── .env.example                  # Environment variable template
├── alembic.ini                   # Alembic migration config
├── Dockerfile                    # Python 3.12-slim container image
├── docker-compose.yml            # Bot + PostgreSQL 16 + Lavalink v4 + Dashboard
├── README.md                     # Complete documentation & user guide
├── core/
│   ├── branding.py               # Embed factory, colors, emojis, Shadow credit
│   ├── cache.py                  # AsyncTTLCache for prefixes & settings
│   ├── checks.py                 # Owner & guild-owner command decorators
│   ├── database.py               # Async SQLAlchemy manager, pooling & backups
│   ├── errors.py                 # Global prefix & slash command error handler
│   ├── events.py                 # Gateway & guild join/remove listeners
│   ├── loader.py                 # Isolated modular Cog discovery & loading
│   ├── logger.py                 # Rotating UTF-8 structured logging
│   ├── permissions.py            # Role hierarchy & dangerous-permission guard
│   └── utilities.py              # Duration parsing, truncation & ConfirmView
├── cogs/
│   └── general/
│       ├── help.py               # Interactive 17-category Help Menu + Search
│       └── core_info.py          # ping, uptime, botinfo, prefix, modules, sync
├── database/
│   ├── models.py                 # 23 normalized SQLAlchemy Async ORM models
│   └── migrations/               # Alembic async migration environment & versions
├── scripts/
│   ├── start.bat                 # Windows CMD launcher
│   ├── start.ps1                 # Windows PowerShell launcher
│   └── start.sh                  # Linux / Linux Mint launcher
├── tests/
│   ├── conftest.py               # Isolated async SQLite test fixture
│   └── test_phase1_foundation.py # Phase 1 automated unit & DB tests
└── logs/                         # Rotating log output directory
```

---

## 10. Troubleshooting Guide

- **`RuntimeError: DISCORD_TOKEN is not configured`**  
  Make sure you copied `.env.example` to `.env` inside `JARVIS/` and replaced `YOUR_DISCORD_BOT_TOKEN` with your real token from the Discord Developer Portal.
- **`PrivilegedIntentsRequired` error on startup**  
  In the Discord Developer Portal (`Bot -> Privileged Gateway Intents`), enable **Presence Intent**, **Server Members Intent**, and **Message Content Intent**, then click **Save Changes**.
- **Slash commands (`/help`, `/ping`) do not show up in Discord**  
  Run `j!sync guild` as the Bot Owner (`BOT_OWNER_IDS` in `.env`) inside your server for instant guild sync, or `j!sync` for global sync (global propagation can take a few minutes).
- **PowerShell refuses to run `Activate.ps1` or `start.ps1`**  
  Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once in PowerShell.
- **Linux Mint `python3 -m venv` fails (`ensurepip is not available`)**  
  Install the venv package first: `sudo apt update && sudo apt install -y python3-venv python3-pip`.
