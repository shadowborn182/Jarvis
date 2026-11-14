# JARVIS — Advanced All-In-One Discord Management Bot

**Bot Name:** JARVIS  
**Developer:** Shadow  
**Language:** Python 3.12+ (3.13 compatible)  
**Discord Library:** `discord.py 2.x`  
**Database:** SQLite (`aiosqlite` default) & PostgreSQL (`asyncpg` optional) via SQLAlchemy 2.0 Async + Alembic  
**Music Engine:** Lavalink v4 (`wavelink`)  
**Web Dashboard:** Python FastAPI + Discord OAuth2  

---

## Table of Contents
1. [Implemented Features & Architecture](#1-implemented-features--architecture)
2. [Discord Developer Portal Setup](#2-discord-developer-portal-setup)
3. [Linux Mint Installation, Migration & Launch Commands](#3-linux-mint-installation-migration--launch-commands)
4. [Windows & Docker Setup](#4-windows--docker-setup)
5. [How to Use JARVIS (Prefix, No Prefix, Slash, Premium, Branding & Dashboard)](#5-how-to-use-jarvis)
6. [Database Migrations & Backups](#6-database-migrations--backups)
7. [Automated Tests](#7-automated-tests)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Implemented Features & Architecture

- **Core Bot & Dynamic Prefix (`bot.py`, `cogs/general/core_info.py`):**
  - `ping`, `uptime`, `botinfo`, `prefix`, `modules`, and owner-only `sync`.
  - Per-server persistent prefixes + rotating presence (`JARVIS | /help`, `Protecting {servers} Servers`, `Developed by Shadow`).
- **No Prefix System (`core/noprefix.py`, `cogs/premium/premium.py`):**
  - Per-server Premium feature (`noprefix enable`, `noprefix disable`, `noprefix toggle`, `noprefix status`).
  - Supports aliases & arguments (`help`, `ping`, `avatar`, `serverinfo`, `userinfo`) with anti-spam sliding-window rate limits and conversation false-positive protection.
- **Per-Server Premium Subscriptions (`core/premium.py`, `cogs/premium/premium.py`):**
  - Per-guild plans (`starter`, `pro`, `enterprise`, `lifetime`), automatic expiration watcher, pre-expiry owner notifications, audit logs, and owner-only `premium grant`, `premium revoke`, `premium extend`, `premium list`, `premium check`.
- **Custom Server Branding & Pillow Banners (`core/branding.py`, `core/banners.py`, `cogs/branding/branding.py`, `cogs/greetings/greetings.py`):**
  - Custom embed hex color, title style (`default`, `uppercase`, `bracketed`, `clean`), custom footer & footer icon, server logo, branding text, welcome/goodbye messages, and Pillow-rendered 1000x360 PNG welcome/goodbye banners with SSRF-protected HTTPS URL validation.
  - *Note:* Per Discord API rules, bots cannot set a different global profile avatar or global banner per server; branding applies to server embeds, welcome/goodbye banners, and dashboard previews.
- **Utility Lookup Commands (`cogs/utility/info.py`):**
  - `avatar` (`av`), `serverinfo` (`si`), and `userinfo` (`ui`, `whois`).
- **Upgraded Interactive Help Menu (`cogs/general/help.py`):**
  - 17-category dropdown, `Back`, `Previous`, `Home`, `Next`, and `Search` modal, live command introspection, Premium & No-Prefix badges, aliases, and permissions.
- **FastAPI Premium Dashboard (`dashboard/app.py`, `dashboard/security.py`):**
  - Discord OAuth2 login, signed HttpOnly sessions, CSRF protection, `Manage Server` permission validation, embed color picker, No Prefix toggle, branding controls, and live PNG banner previews.

---

## 2. Discord Developer Portal Setup

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and create/open **JARVIS**.
2. Go to **Bot -> Privileged Gateway Intents** and enable:
   - **Presence Intent**
   - **Server Members Intent**
   - **Message Content Intent** (required for Prefix & No-Prefix commands)
3. Copy your Bot Token into `.env` (`DISCORD_TOKEN`).
4. Go to **OAuth2 -> General**, copy `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`, and add Redirect URI `http://localhost:8080/auth/callback`.
5. Invite the bot via **OAuth2 -> URL Generator** (`bot` + `applications.commands`).

---

## 3. Linux Mint Installation, Migration & Launch Commands

Run these exact commands in your Linux Mint terminal:

```bash
# 1. Install Python venv & Pillow system dependencies (if not already installed)
sudo apt update && sudo apt install -y python3 python3-venv python3-pip libjpeg-dev zlib1g-dev fonts-dejavu-core

# 2. Enter the JARVIS project directory
cd JARVIS

# 3. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install all Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create and edit your .env configuration
cp .env.example .env
nano .env
# Set DISCORD_TOKEN, BOT_OWNER_IDS, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET,
# SESSION_SECRET, and CSRF_SECRET. Default DATABASE_URL uses local SQLite.

# 6. Run Alembic database migrations (safe for existing data)
alembic upgrade head

# 7. Start the JARVIS Discord bot
python bot.py
```

### Start the FastAPI Premium Dashboard (in a second Linux Mint terminal)
```bash
cd JARVIS
source .venv/bin/activate
uvicorn dashboard.app:app --host 0.0.0.0 --port 8080
```
Then open `http://localhost:8080` in your browser.

---

## 4. Windows & Docker Setup

- **Windows PowerShell:** `.\scripts\start.ps1` (or `python -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`, `alembic upgrade head`, `python bot.py`).
- **Windows CMD:** `scripts\start.bat`.
- **Docker Compose:** `cp .env.example .env && docker compose up -d --build`.

---

## 5. How to Use JARVIS

1. **Sync Slash Commands (Bot Owner):**
   Run `j!sync guild` inside your server (or `j!sync` globally).
2. **Grant Server Premium (Bot Owner):**
   Run `j!premium grant <guild_id> pro 30d` (or `lifetime`).
3. **Enable No-Prefix (Server Admin with Manage Server):**
   Run `j!noprefix enable` or toggle it in the Web Dashboard.
   Then members can type `help`, `ping`, `avatar @user`, `userinfo`, `serverinfo` without any prefix.
4. **Customize Server Branding & Banners (Server Admin):**
   - `j!brand color #38BDF8`
   - `j!brand footer "My Community" https://example.com/icon.png`
   - `j!brand welcome "Welcome {mention} to {server}!"`
   - `j!brand preview welcome`
   - `j!welcome channel #welcome`

---

## 6. Database Migrations & Backups

- Existing guild and user rows are preserved across upgrades (`0001_initial_schema` -> `0002_premium_branding_noprefix`).
- Apply migrations anytime with:
  ```bash
  alembic upgrade head
  ```

---

## 7. Automated Tests

Run the full automated test suite inside your virtual environment:
```bash
cd JARVIS
pytest -v
```

---

## 8. Troubleshooting

- **No-Prefix commands do not respond:** Verify **Message Content Intent** is enabled in Discord Developer Portal, the server has active Premium (`j!premium status`), and No Prefix is enabled (`j!noprefix status`).
- **Dashboard returns 503 on Login:** Ensure `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, and `DISCORD_REDIRECT_URI` are set in `.env`.
- **Custom banner URL rejected:** Only `https://` URLs pointing to public hosts returning PNG, JPG, JPEG, or WEBP under 5 MB are accepted.
