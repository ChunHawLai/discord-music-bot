# Hosting Guide — 4 Options

A Discord bot must run on a computer 24/7. Here are four ways to do it, from easiest to most control.

> ⚠️ **Never commit your `.env` file.** Your bot token is a secret. On hosted platforms, set it as an environment variable / secret in the platform's dashboard, not in the code.

---

## Option 1 — Bot-Hosting.net (FREE + simplest) ⭐ Recommended for most people

**Cost:** $0/month, no credit card. **Effort:** ~5 minutes.

- Free plan: 256 MB RAM, 25% CPU, 512 MB storage, 1 deployment
- Runs 24/7, auto-restarts on crash, installs `requirements.txt` automatically
- **Catch:** you must click "Renew" in the panel every 4 days (free plans do this to reclaim unused resources)

### Steps
1. Sign up at **https://bot-hosting.net** (Discord login works).
2. **New Deployment** → type **Discord Bot** or **Python** → source **Archive/ZIP**.
3. Upload `music-bot-deploy.zip` (contains only `bot.py` + `requirements.txt`).
   - Or connect this GitHub repo instead.
4. Set **Startup / entry file** to `bot.py`.
5. Go to **Environment** → add a **secret**:
   - `DISCORD_TOKEN` = your bot token
6. Click **Start**. Check the **Console** for `Logged in as ...`, then test `!play never gonna give you up`.

**Note:** 256 MB is modest. If you see out-of-memory errors, either upgrade to the $2.69 plan or optimize. Most simple bots fit fine.

---

## Option 2 — Fly.io (effectively free, most reliable)

**Cost:** ~$2.21/month for a 24/7 bot, but **Fly waives any bill under $5** → you pay $0. **Requires a credit card** on file (not charged). **Effort:** ~15 minutes.

A `Dockerfile` and `fly.toml` are included in this repo, so deployment is straightforward.

### Steps
1. Install Fly CLI:
   ```powershell
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```
2. Sign up / log in:
   ```powershell
   fly auth signup    # or: fly auth login
   ```
3. From this folder, launch (accept defaults; don't deploy yet if asked):
   ```powershell
   fly launch --no-deploy
   ```
4. Set your token as a secret:
   ```powershell
   fly secrets set DISCORD_TOKEN=your_bot_token_here
   ```
5. Deploy:
   ```powershell
   fly deploy
   ```
6. Check logs:
   ```powershell
   fly logs
   ```

The Dockerfile installs FFmpeg and Python dependencies automatically. The `fly.toml` uses the smallest shared-CPU VM (512 MB), which keeps the bill well under the $5 waiver threshold.

---

## Option 3 — Oracle Cloud Always-Free VPS (truly free forever)

**Cost:** $0 forever. **Effort:** ~45 minutes. Generous free tier: 4 ARM CPUs, 24 GB RAM.

Signup requires a credit card for identity verification, but you are never charged if you stay within the Always Free limits.

### Steps
1. Create a free account at **https://www.oracle.com/cloud/free/**.
2. In the Console: **Compute → Instances → Create Instance**.
   - Image: **Ubuntu 22.04** (ARM/Ampere shape)
   - Shape: **VM.Standard.A1.Flex** (Always Free eligible) — set to 4 OCPU / 24 GB (or less)
   - Add your SSH public key (or generate one)
3. Once running, note the **public IP** and connect via SSH:
   ```bash
   ssh ubuntu@YOUR_PUBLIC_IP
   ```
4. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv ffmpeg git
   ```
5. Get the code onto the server:
   ```bash
   git clone https://github.com/YOUR_USERNAME/discord-music-bot.git
   cd discord-music-bot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
6. Create a `.env` file with your token:
   ```bash
   nano .env
   ```
   ```
   DISCORD_TOKEN=your_bot_token_here
   FFMPEG_EXECUTABLE=ffmpeg
   ```
7. Run it in the background so it survives logout:
   ```bash
   nohup .venv/bin/python bot.py > bot.log 2>&1 &
   ```
   Verify with `tail -f bot.log`.

**Better long-term:** run it as a systemd service so it auto-starts on reboot. Ask me if you want the service file.

---

## Option 4 — Your own PC (free, you control it)

**Cost:** $0 (uses your electricity). **Effort:** 1 minute. **Catch:** PC must stay on.

### Windows
- Double-click **`START BOT.bat`** (or the "Music Bot" desktop shortcut).
- To auto-start on login: `Win + R` → `shell:startup` → create a shortcut to `START BOT.bat` in that folder.

### Linux / macOS
```bash
cd discord-music-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
nohup python bot.py > bot.log 2>&1 &
```

---

## Comparison

| Option | Cost | Setup | Uptime | Notes |
| --- | --- | --- | --- | --- |
| **Bot-Hosting.net** | Free | Easiest | 24/7 | Renew every 4 days; 256 MB RAM |
| **Fly.io** | $0 (bill waived) | Easy | 24/7 | Credit card needed; very reliable |
| **Oracle Cloud** | Free forever | Moderate | 24/7 | Most powerful; free VPS |
| **Your PC** | Free | Easy | While PC is on | Full control; no hosting account |

---

## Troubleshooting on a host

- **"davey library needed"** → add `davey==0.1.7` to `requirements.txt` (already there for Python 3.10; on 3.11+ a newer wheel may be picked automatically).
- **"ffmpeg not found"** → the host doesn't have FFmpeg. On Fly.io the Dockerfile installs it. On Oracle/PC install it via `apt install ffmpeg` / `winget install Gyan.FFmpeg`.
- **"Improper token" / no response** → check that `DISCORD_TOKEN` is set as a secret and the Message Content Intent is enabled in the Developer Portal.
- **yt-dlp stops working** → YouTube changes periodically; run `pip install -U yt-dlp`.
