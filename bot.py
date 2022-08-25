from discord.ext import commands
from discord import Intents
import motor.motor_asyncio as motor
import tomli

import logging
import os

from modules.help import PretenderHelpCommand
from modules.cooldown import apply_cooldowns

logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    
    handlers=[
        logging.FileHandler(filename="discord.log", encoding="utf-8"),
        logging.StreamHandler() # for printing stuff to the console
    ]
)

with open("config.toml", "rb") as file:
    config = tomli.load(file)

intents = Intents.default()
intents.members = True # needed for $count

bot = commands.Bot(command_prefix=config["prefix"], help_command=PretenderHelpCommand(), intents=intents)
bot.config = config # for global cog access

# database thingies
client = motor.AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_URI"))
bot.database = client.get_default_database("pretender")

# loading cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.counting")
bot.load_extension("cogs.opting")
bot.load_extension("cogs.events")

bot.load_extension("jishaku")

# applying cooldowns
apply_cooldowns(bot.config["Cooldowns"]["Durations"], bot.commands)

bot.run(os.getenv("DISCORD_TOKEN"))
