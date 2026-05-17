import asyncio
import os
import subprocess
from typing import Optional

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from mcstatus import JavaServer

load_dotenv()

TOKEN: str = os.environ["DISCORD_TOKEN"]
CHANNEL_ID: int = int(os.environ["DISCORD_CHANNEL_ID"])
MC_HOST: str = os.getenv("MC_HOST", "localhost")
MC_PORT: int = int(os.getenv("MC_PORT", "25565"))
JAR_PATH: str = os.environ["JAR_PATH"]
JAVA_ARGS: str = os.getenv("JAVA_ARGS", "-Xmx2G -Xms1G")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

mc_server = JavaServer(MC_HOST, MC_PORT)
server_process: Optional[subprocess.Popen] = None
last_online: Optional[bool] = None
last_ip: Optional[str] = None


async def is_server_online() -> tuple[bool, int]:
    try:
        status = await asyncio.wait_for(mc_server.async_status(), timeout=10)
        return True, status.players.online
    except Exception:
        return False, 0


async def get_public_ip() -> Optional[str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.ipify.org",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                return (await resp.text()).strip()
    except Exception:
        return None


@bot.event
async def on_ready():
    global last_ip
    print(f"Logged in as {bot.user} ({bot.user.id})")
    last_ip = await get_public_ip()
    if not monitor_server.is_running():
        monitor_server.start()
    if not monitor_ip.is_running():
        monitor_ip.start()


@tasks.loop(seconds=60)
async def monitor_server():
    global last_online
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return

    online, players = await is_server_online()

    if last_online is None:
        last_online = online
        return

    if online != last_online:
        last_online = online
        if online:
            await channel.send(
                f"✅ Minecraft server is now **ONLINE**! Players online: {players}"
            )
        else:
            await channel.send("❌ Minecraft server is now **OFFLINE**.")


@monitor_server.before_loop
async def before_monitor_server():
    await bot.wait_until_ready()


@tasks.loop(seconds=60)
async def monitor_ip():
    global last_ip
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return

    current_ip = await get_public_ip()
    if current_ip is None:
        return

    if last_ip is not None and current_ip != last_ip:
        last_ip = current_ip
        await channel.send(
            f"@everyone The server's public IP has changed!\n"
            f"New address: `{current_ip}:{MC_PORT}`",
            allowed_mentions=discord.AllowedMentions(everyone=True),
        )
    else:
        last_ip = current_ip


@monitor_ip.before_loop
async def before_monitor_ip():
    await bot.wait_until_ready()


@bot.command()
@commands.has_permissions(administrator=True)
async def start(ctx: commands.Context):
    global server_process

    if server_process is not None and server_process.poll() is None:
        await ctx.send("The server is already running!")
        return

    jar_dir = os.path.dirname(os.path.abspath(JAR_PATH))
    jar_name = os.path.basename(JAR_PATH)
    java_args = JAVA_ARGS.split()

    try:
        server_process = subprocess.Popen(
            ["java", *java_args, "-jar", jar_name, "nogui"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=jar_dir,
        )
        await ctx.send(
            "🚀 Starting the Minecraft server... give it a minute to come online."
        )
    except FileNotFoundError:
        await ctx.send(
            "❌ Could not find `java`. Make sure Java is installed and on your PATH."
        )
    except Exception as e:
        await ctx.send(f"❌ Failed to start server: {e}")


@bot.command()
@commands.has_permissions(administrator=True)
async def stop(ctx: commands.Context):
    global server_process

    online, _ = await is_server_online()
    if not online:
        await ctx.send("The server is not currently online.")
        return

    if server_process is not None and server_process.poll() is None:
        try:
            server_process.stdin.write(b"stop\n")
            server_process.stdin.flush()
            await ctx.send("🛑 Sent stop command to the server.")
        except Exception as e:
            await ctx.send(f"❌ Failed to send stop command: {e}")
    else:
        await ctx.send(
            "⚠️ The server is running but wasn't started by this bot session. "
            "Please stop it manually."
        )


@bot.command()
async def status(ctx: commands.Context):
    online, players = await is_server_online()
    ip = last_ip or "Unknown"

    if online:
        await ctx.send(
            f"✅ **Server is ONLINE**\n"
            f"Players: {players}\n"
            f"IP: `{ip}:{MC_PORT}`"
        )
    else:
        await ctx.send(
            f"❌ **Server is OFFLINE**\n"
            f"Last known IP: `{ip}:{MC_PORT}`"
        )


@start.error
@stop.error
async def admin_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permission to use that command.")


bot.run(TOKEN)
