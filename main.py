import os
import discord
from dotenv import load_dotenv

from bot.Client import Client

load_dotenv()
if os.getenv("BOT_TOKEN") is None:
    print("Discord Bot Token not set.")
    exit()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)
client.run(BOT_TOKEN)