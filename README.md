# Discord Music Bot (YouTube)

A Discord bot that searches and plays audio from YouTube, with a queue. Built with **discord.py** and **yt-dlp**.

🔗 **Repository:** https://github.com/ChunHawLai/discord-music-bot

## Commands

| Command | Description |
| --- | --- |
| `!play <song or URL>` | Play ONE song (a playlist link plays only its first song) |
| `!playlist <URL>` | Add ALL songs from a playlist URL to the queue |
| `!pause` | Pause playback |
| `!resume` | Resume playback |
| `!skip` | Skip the current song |
| `!stop` | Stop and clear the queue |
| `!queue` | Show the queue |
| `!volume <0-100>` | Set volume |
| `!join` | Join your voice channel |
| `!leave` | Leave the voice channel |
| `!help` | Show all commands |

---

## Quick start (your own PC)

1. **Discord setup**
   - Create an app/bot at https://discord.com/developers/applications
   - Copy the bot token
   - Enable **Message Content Intent** on the Bot tab → **Save Changes**
   - Invite with `bot` scope + **Send Messages, Embed Links, Connect, Speak**

2. **Install FFmpeg**
   - Windows: `winget install Gyan.FFmpeg`

3. **Install Python packages**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Configure** — copy `.env.example` to `.env` and set:
   ```
   DISCORD_TOKEN=your_bot_token_here
   FFMPEG_EXECUTABLE=ffmpeg
   ```

5. **Run** — double-click `START BOT.bat` (Windows) or:
   ```powershell
   .\.venv\Scripts\python.exe bot.py
   ```

---

## Hosting (24/7, without leaving your PC on)

See **[HOSTING.md](HOSTING.md)** for full guides:

| Option | Cost | Effort |
| --- | --- | --- |
| **Bot-Hosting.net** | Free | Easiest — upload a ZIP |
| **Fly.io** | $0 (bill waived under $5) | Easy — `fly deploy`, configs included |
| **Oracle Cloud Always Free** | Free forever | Moderate — free VPS |
| **Your own PC** | Free | Easy — `START BOT.bat` |

---

## Files

| File | Purpose |
| --- | --- |
| `bot.py` | Bot logic and commands |
| `requirements.txt` | Python dependencies (pinned working versions) |
| `.env.example` | Template for secrets (never commit `.env`) |
| `START BOT.bat` | Windows one-click launcher |
| `HOSTING.md` | Deployment guides for 4 hosting options |
| `Dockerfile` / `fly.toml` | Fly.io deployment config |
| `.gitignore` / `.dockerignore` | Keep secrets and junk out of git/Docker |

---

## Notes

- The bot automatically leaves the voice channel **10 seconds after the last person leaves**.
- Audio is **streamed**, not downloaded, so it uses little disk.
- Age-restricted / members-only videos may fail — a YouTube limitation.
- YouTube changes periodically and can break `yt-dlp`. Fix: `pip install -U yt-dlp`.
- If Discord changes its voice protocol, keep `davey` installed (`davey>=0.1.0`), used by discord.py 2.7+ for voice encryption.
