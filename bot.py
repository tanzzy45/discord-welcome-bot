# bot.py
import os
import json
import threading
from dotenv import load_dotenv
import discord
from discord.ext import commands
from flask import Flask

# ----------------- Load env -----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: DISCORD_TOKEN not found. Add it to .env or environment variables.")

WELCOME_CHANNEL_NAME = os.getenv("WELCOME_CHANNEL_NAME", "general")
DATA_FILE = os.getenv("DATA_FILE", "user_data.json")

# ----------------- Load seen-users -----------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        seen_users = json.load(f)
else:
    seen_users = {}  # { guild_id_str: [user_id_str, ...] }

# ----------------- Discord bot setup -----------------
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id={bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    if guild_id not in seen_users:
        seen_users[guild_id] = []

    if user_id not in seen_users[guild_id]:
        seen_users[guild_id].append(user_id)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_users, f, indent=2)

        welcome_channel = discord.utils.get(message.guild.text_channels, name=WELCOME_CHANNEL_NAME)
        if welcome_channel:
            await welcome_channel.send(f"👋 Welcome {message.author.mention} to **{message.guild.name}**! 🎉")
        else:
            await message.channel.send(f"👋 Welcome {message.author.mention} to **{message.guild.name}**! 🎉")

    await bot.process_commands(message)

# ----------------- Tiny web server for Render -----------------
app = Flask("render_ping")

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ----------------- Start both Discord bot and web server -----------------
if __name__ == "__main__":
    # Start web server in a separate thread
    threading.Thread(target=run_web).start()
    # Start Discord bot (blocking)
    bot.run(TOKEN)
