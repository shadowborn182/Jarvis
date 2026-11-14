# JARVIS — Advanced All-In-One Discord Management Bot

**Developer:** Shadow  
**Language:** Python 3.12+ (3.13 compatible) · **Library:** `discord.py 2.x`  
**Database:** SQLite (Local Development) / PostgreSQL (Production) via SQLAlchemy Async & Alembic  
**Music Engine:** Lavalink v4 (`wavelink`) · **Dashboard:** FastAPI + Discord OAuth2

---

## Architecture Overview

JARVIS uses a modular Cog-based architecture under `cogs/` backed by a shared asynchronous service layer in `core/` and normalized SQLAlchemy 2.0 ORM models in `database/`.

### 17 Official Modules
1. **Security** — Anti-nuke, anti-raid, anti-betray, quarantine, panic & night mode
2. **Utility** — Server/user info, reminders, polls, sticky messages, embed builder
3. **General** — Interactive help menu, bot stats, XP leveling, profiles & badges
4. **Moderation** — Ban, tempban, kick, warn, timeout, purge, channel locks, voice mod
5. **Autoroles** — Join/bot/human autoroles, button roles, dropdown roles, reaction panels
6. **Fun** — Mini-games, 8ball, Tic-Tac-Toe, Connect Four, social actions
7. **Greetings** — Custom welcome/goodbye banners, embeds, DMs, boost alerts
8. **Giveaway** — Multi-winner timed giveaways with role filters & restart-safe buttons
9. **Ticket** — Multi-category support panels, claim/close workflows, HTML transcripts
10. **Music** — Lavalink v4 playback, queues, audio filters, 24/7 mode & playlists
11. **Tracker** — Join, leave, boost, invite, message & voice analytics
12. **Logging** — Granular event audit channels with exclusions & actor tracking
13. **Birthdays** — Timezone-aware birthday wishes, roles & upcoming lists
14. **Customrole** — Personal user roles with hierarchy & dangerous-permission protection
15. **Template** — Server structure, role & embed JSON backup/restore templates
16. **Marriage** — Proposals, marriage profiles, anniversaries & couple leaderboards
17. **Premium** — Subscription plans, server slots & automatic expiry management

---

## Discord Developer Portal Setup

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and create an application named **JARVIS**.
2. Under **Bot**, enable all required **Privileged Gateway Intents**:
   - **Presence Intent**
   - **Server Members Intent**
   - **Message Content Intent**
3. Copy the Bot Token into `.env` as `DISCORD_TOKEN`.
4. Under **OAuth2 -> General**, copy Client ID (`DISCORD_CLIENT_ID`) and Client Secret (`DISCORD_CLIENT_SECRET`), and add your dashboard redirect URL (`http://localhost:8080/auth/callback`).
5. Under **OAuth2 -> URL Generator**, select scopes `bot` and `applications.commands`, and grant `Administrator` (or granular management permissions) to generate your invite URL.

---

## Installation & Running

### Windows Command Prompt (CMD)
```bat
cd JARVIS
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python bot.py
```
Or run `scripts\start.bat`.

### Windows PowerShell
```powershell
cd JARVIS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python bot.py
```
Or run `.\scripts\start.ps1`.

### Linux / Linux Mint
```bash
cd JARVIS
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python bot.py
```
Or run `chmod +x scripts/start.sh && ./scripts/start.sh`.

### Docker (Bot + PostgreSQL 16 + Lavalink v4 + FastAPI Dashboard)
```bash
cd JARVIS
cp .env.example .env
docker compose up -d --build
```

---

## Testing

Run the automated test suite with `pytest`:
```bash
pytest -v
```
