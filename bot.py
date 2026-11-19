"""A Discord music bot that searches and plays audio from YouTube.

Commands:
    !play <query or url>   Search YouTube (or play a URL) and add to the queue
    !pause                 Pause playback
    !resume                Resume playback
    !skip                  Skip the current song
    !stop                  Stop and clear the queue
    !queue                 Show the queue
    !volume <0-100>        Set volume
    !join                  Join your voice channel
    !leave                 Leave the voice channel
"""

import asyncio
import os

import discord
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
TOKEN = os.getenv("DISCORD_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.message_content = True  # Required so the bot can read !play messages

bot = commands.Bot(command_prefix="!", intents=INTENTS)

FFMPEG_EXECUTABLE = os.getenv("FFMPEG_EXECUTABLE", "ffmpeg")

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "extract_flat": False,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

queues: dict[int, list[dict]] = {}
volumes: dict[int, float] = {}


# --------------------------------------------------------------------------- #
# Audio source
# --------------------------------------------------------------------------- #
class YTDLSource(discord.PCMVolumeTransformer):
    """A discord.py audio source backed by a streamed YouTube URL."""

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title", "Unknown title")
        self.url = data.get("url")
        self.webpage_url = data.get("webpage_url")
        self.duration = data.get("duration")

    @classmethod
    async def from_url(cls, url: str, *, volume: float = 0.5):
        """Extract audio info without downloading, then build a streaming source."""
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        if not data:
            raise ValueError("No results found.")
        if "entries" in data:
            entries = [e for e in data["entries"] if e]
            if not entries:
                raise ValueError("No results found.")
            data = entries[0]
        if not data.get("url"):
            raise ValueError("This video cannot be streamed.")
        source = discord.FFmpegPCMAudio(
            data["url"], executable=FFMPEG_EXECUTABLE, **FFMPEG_OPTIONS
        )
        return cls(source, data=data, volume=volume)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def get_queue(guild_id: int) -> list[dict]:
    return queues.setdefault(guild_id, [])


def get_volume(guild_id: int) -> float:
    return volumes.get(guild_id, 0.5)


async def ensure_voice(ctx: commands.Context) -> bool:
    """Make sure the author is in a voice channel and the bot is connected."""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You need to join a voice channel first.")
        return False
    channel = ctx.author.voice.channel
    vc = ctx.voice_client
    if vc is None:
        await channel.connect()
        vc = ctx.voice_client
        if vc is None:
            await ctx.send("❌ Could not connect to voice. Please try again.")
            return False
    elif vc.channel != channel:
        await vc.move_to(channel)
    return True


def after_playback(ctx: commands.Context, error):
    """Called by discord.py in a background thread when a song finishes."""
    if error:
        print(f"Playback error: {error}")
    asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)


async def play_next(ctx: commands.Context, *, announce: bool = True):
    """Play the next song in this guild's queue, if any."""
    queue = get_queue(ctx.guild.id)
    vc = ctx.voice_client
    if vc is None or not queue:
        return

    song = queue.pop(0)
    try:
        source = await YTDLSource.from_url(
            song["web_url"], volume=get_volume(ctx.guild.id)
        )
    except Exception as exc:  # noqa: BLE001
        await ctx.send(f"❌ Could not play **{song['title']}**: {exc}")
        await play_next(ctx)
        return

    vc.play(source, after=lambda err: after_playback(ctx, err))
    if announce:
        await ctx.send(f"🎵 Now playing: **{source.title}**")


# --------------------------------------------------------------------------- #
# Events
# --------------------------------------------------------------------------- #
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
@bot.command(name="join", aliases=["connect"])
async def join(ctx: commands.Context):
    if await ensure_voice(ctx):
        await ctx.send(f"🔊 Joined **{ctx.author.voice.channel.name}**.")


@bot.command(name="play", aliases=["p"])
async def play(ctx: commands.Context, *, query: str):
    if not query:
        await ctx.send("⚠️ Give me a song name or YouTube URL. Example: `!play never gonna give you up`")
        return
    if not await ensure_voice(ctx):
        return

    search_msg = await ctx.send("🔎 Searching YouTube...")
    try:
        source = await YTDLSource.from_url(query, volume=get_volume(ctx.guild.id))
    except Exception as exc:  # noqa: BLE001
        await search_msg.edit(content=f"❌ Couldn't find or play that: {exc}")
        return

    queue = get_queue(ctx.guild.id)
    queue.append({
        "web_url": source.webpage_url or source.url,
        "title": source.title,
        "duration": source.duration,
        "requester": ctx.author.display_name,
    })

    vc = ctx.voice_client
    if vc and (vc.is_playing() or vc.is_paused()):
        await search_msg.edit(
            content=f"✅ Added to queue (#{len(queue)}): **{source.title}**"
        )
    else:
        await search_msg.edit(content=f"🎵 Now playing: **{source.title}**")
        await play_next(ctx, announce=False)


@bot.command(name="pause")
async def pause(ctx: commands.Context):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️ Paused.")
    else:
        await ctx.send("❌ Nothing is playing right now.")


@bot.command(name="resume")
async def resume(ctx: commands.Context):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶️ Resumed.")
    else:
        await ctx.send("❌ Nothing is paused right now.")


@bot.command(name="skip", aliases=["next"])
async def skip(ctx: commands.Context):
    vc = ctx.voice_client
    if vc and (vc.is_playing() or vc.is_paused()):
        vc.stop()
        await ctx.send("⏭️ Skipped.")
    else:
        await ctx.send("❌ Nothing is playing right now.")


@bot.command(name="stop")
async def stop(ctx: commands.Context):
    get_queue(ctx.guild.id).clear()
    vc = ctx.voice_client
    if vc:
        vc.stop()
    await ctx.send("⏹️ Stopped and cleared the queue.")


@bot.command(name="queue", aliases=["q"])
async def show_queue(ctx: commands.Context):
    queue = get_queue(ctx.guild.id)
    if not queue:
        await ctx.send("📭 The queue is empty.")
        return
    lines = []
    for i, song in enumerate(queue[:20], start=1):
        duration = song.get("duration")
        length = f" ({duration // 60}:{duration % 60:02d})" if duration else ""
        lines.append(f"`{i}.` **{song['title']}**{length} — {song['requester']}")
    await ctx.send(embed=discord.Embed(title="📋 Music Queue", description="\n".join(lines)))


@bot.command(name="volume")
async def volume(ctx: commands.Context, level: int):
    if not 0 <= level <= 100:
        await ctx.send("⚠️ Volume must be between 0 and 100.")
        return
    new_volume = level / 100
    volumes[ctx.guild.id] = new_volume
    vc = ctx.voice_client
    if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
        vc.source.volume = new_volume
    await ctx.send(f"🔊 Volume set to **{level}%**.")


@bot.command(name="leave", aliases=["disconnect", "dc"])
async def leave(ctx: commands.Context):
    get_queue(ctx.guild.id).clear()
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send("👋 Left the voice channel.")
    else:
        await ctx.send("❌ I'm not in a voice channel.")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set in .env.")
    bot.run(TOKEN)
