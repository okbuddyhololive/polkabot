from discord.ext import commands
from discord import Intents
import toml

import logging
import os

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

bot = commands.Bot(command_prefix=config["prefix"], intents=Intents.default())
bot.config = config # for global cog access

# loading cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.events")
bot.load_extension("jishaku")

bot.run(os.getenv("DISCORD_TOKEN"))