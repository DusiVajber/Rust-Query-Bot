import discord
from discord import app_commands
import a2s
import json
import os
from dotenv import load_dotenv
import aiohttp
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DATA_FILE = "servers.json"

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
        info = a2s.info((ip, port), timeout=3.0)
        await interaction.response.send_message(
            f"🌍 `{info.server_name}`\n👥 Players: {info.player_count}/{info.max_players}"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to fetch server info: {e}")

# --- /map Command ---
@tree.command(name="map", description="Get RustMaps link via BattleMetrics")
@app_commands.describe(name="Name of the linked server")
async def map_cmd(interaction: discord.Interaction, name: str):
    if name not in servers:
        await interaction.response.send_message("❌ Server name not found. Use `/link` first.")
        return

    ip, port = servers[name]
    port = int(port)

    await interaction.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Get server ID from BattleMetrics API
            api_url = f"https://api.battlemetrics.com/servers?filter[game]=rust&filter[search]={ip}:{port}"
            async with session.get(api_url) as resp:
                data = await resp.json()

                for server in data.get("data", []):
                    attr = server["attributes"]
                    if attr.get("ip") == ip and attr.get("port") == port:
                        server_id = server["id"]

                        # Step 2: Fetch BattleMetrics server page HTML
                        html_url = f"https://www.battlemetrics.com/servers/rust/{server_id}"
                        async with session.get(html_url) as page_resp:
                            html_content = await page_resp.text()

                            # Step 3: Parse HTML and find rustmaps.com link
                            soup = BeautifulSoup(html_content, "html.parser")
                            rustmaps_link = None
                            for a in soup.find_all("a", href=True):
                                href = a['href']
                                if "rustmaps.com/map/" in href:
                                    rustmaps_link = href
                                    break

                            if rustmaps_link:
                                await interaction.followup.send(f"🗺️ RustMaps link: {rustmaps_link}")
                            else:
                                await interaction.followup.send(
                                    f"⚠️ RustMaps link not found on the page.\n🔗 {html_url}"
                                )
                        return

                await interaction.followup.send("❌ Exact IP/port match not found in BattleMetrics.")
    except Exception as e:
        await interaction.followup.send(f"❌ Exception: {type(e).__name__}: {e}")

# --- /wipe Command ---
@tree.command(name="wipe", description="Show server's last wipe estimate (disabled, uptime unsupported)")
@app_commands.describe(name="Name of the linked server")
async def wipe(interaction: discord.Interaction, name: str):
    await interaction.response.send_message("⚠️ Rust servers do not expose uptime over A2S. Try using an API like BattleMetrics.")

# --- /list Command ---
@tree.command(name="list", description="List all linked servers")
async def list_cmd(interaction: discord.Interaction):
    if not servers:
        await interaction.response.send_message("📭 No linked servers yet.")
        return

    msg = "\n".join([f"🔗 `{name}` → `{ip}:{port}`" for name, (ip, port) in servers.items()])
    await interaction.response.send_message(f"**Linked servers:**\n{msg}")

# --- On Ready ---
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user}")

client.run(TOKEN)
