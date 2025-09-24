# bot.py
import os
import json
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load .env from current directory (you can pass path: load_dotenv('/path/to/.env'))
load_dotenv()

# --- CONFIG from env (with sensible defaults) ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: DISCORD_TOKEN not found. Add it to .env or environment variables.")

WELCOME_CHANNEL_NAME = os.getenv("WELCOME_CHANNEL_NAME", "general")
DATA_FILE = os.getenv("DATA_FILE", "user_data.json")

# --- Load seen-users data ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        seen_users = json.load(f)
else:
    seen_users = {}  # { guild_id_str: [user_id_str, ...] }

# --- Discord bot setup ---
intents = discord.Intents.default()
intents.messages = True    # we only need message events (not reading message content)
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (id={bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.guild is None:
        return  # ignore DMs

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    if guild_id not in seen_users:
        seen_users[guild_id] = []

    if user_id not in seen_users[guild_id]:
        # mark seen and persist
        seen_users[guild_id].append(user_id)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_users, f, indent=2)

        # prefer to send in dedicated welcome channel if it exists
        welcome_channel = discord.utils.get(message.guild.text_channels, name=WELCOME_CHANNEL_NAME)
        if welcome_channel:
            await welcome_channel.send(f"👋 Welcome {message.author.mention} to **{message.guild.name}**! 🎉")
        else:
            # fallback: send in the channel they typed in
            await message.channel.send(f"👋 Welcome {message.author.mention} to **{message.guild.name}**! 🎉")

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(TOKEN)
