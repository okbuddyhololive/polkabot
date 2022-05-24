from discord.ext import commands
from discord import Intents
import motor.motor_asyncio as motor
import toml

import logging
import os

from modules.help import PretenderHelpCommand

logger = logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    
    handlers=[
        logging.FileHandler(filename="discord.log", encoding="utf-8"),
        logging.StreamHandler() # for printing stuff to the console
    ]
)

with open("config.toml") as file:
    config = toml.load(file)

intents = Intents.default()
intents.members = True # needed for $count

bot = commands.Bot(command_prefix=config["prefix"], help_command=PretenderHelpCommand(), intents=intents)
bot.config = config # for global cog access

# database thingies
uri = os.getenv("MONGODB_CONNECTION_URI")
#name = uri.rsplit("/", 1)[-1]
name = "pretender"

client = motor.AsyncIOMotorClient(uri)
bot.database = client[name]

# loading cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.counting")
bot.load_extension("cogs.events")

bot.load_extension("jishaku")

bot.run(os.getenv("DISCORD_TOKEN"))