import discord
from discord import app_commands
import a2s
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DATA_FILE = "servers.json" # File to store linked servers

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# Load or initialize server data
def load_servers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_servers(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


servers = load_servers()


# --- /link Command ---
@tree.command(name="link", description="Link a name to a Rust server (IP:port)")
@app_commands.describe(name="Name for the server", address="IP:port of the server")
async def link(interaction: discord.Interaction, name: str, address: str):
    try:
        ip, port = address.split(":")
        port = int(port)
        servers[name] = [ip, port]
        save_servers(servers)
        await interaction.response.send_message(f"🔗 Linked `{name}` to `{ip}:{port}`.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")


# --- /pop Command ---
@tree.command(name="pop", description="Get Rust server population")
@app_commands.describe(name="Name of the linked server")
async def pop(interaction: discord.Interaction, name: str):
    if name not in servers:
        await interaction.response.send_message("❌ Server name not found. Use `/link` first.")
        return

    try:
        ip, port = servers[name]
        info = a2s.info((ip, port))
        await interaction.response.send_message(
            f"🌍 `{info.server_name}`\n👥 Players: {info.player_count}/{info.max_players}"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to fetch server info: {e}")


# --- /wipe Command ---
@tree.command(name="wipe", description="Estimate last wipe time (server uptime)")
@app_commands.describe(name="Name of the linked server")
async def wipe(interaction: discord.Interaction, name: str):
    if name not in servers:
        await interaction.response.send_message("❌ Server name not found. Use `/link` first.")
        return

    try:
        ip, port = servers[name]
        info = a2s.info((ip, port))
        uptime_seconds = info.server_uptime
        if uptime_seconds:
            wiped_time = datetime.utcnow() - timedelta(seconds=uptime_seconds)
            await interaction.response.send_message(
                f"🧹 Estimated last wipe: `{wiped_time.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n(Uptime: {uptime_seconds//3600}h)"
            )
        else:
            await interaction.response.send_message("⚠️ Uptime not available.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to get wipe time: {e}")


# --- /map Command ---
@tree.command(name="map", description="Show map of the server (external link)")
@app_commands.describe(name="Name of the linked server")
async def map_cmd(interaction: discord.Interaction, name: str):
    if name not in servers:
        await interaction.response.send_message("❌ Server name not found. Use `/link` first.")
        return

    ip, port = servers[name]
    # You can replace this link with any third-party tracking service
    map_url = f"https://battlemetrics.com/servers/rust?q={ip}"
    await interaction.response.send_message(f"🗺️ Map link: {map_url}")


# --- On Ready ---
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user}")


client.run(TOKEN)
