from discord.ext import commands
from discord import Intents
import motor.motor_asyncio as motor
import dotenv
import tomli

import logging
import os

from modules.help import PretenderHelpCommand
from modules.cooldown import apply_cooldowns

# load the environment file 
dotenv.load_dotenv()

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    
    handlers=[
        logging.FileHandler(filename="discord.log", encoding="utf-8"),
        logging.StreamHandler() # for printing stuff to the console
    ]
)

# load the config file
with open("config.toml", "rb") as file:
    config = tomli.load(file)

# create the bot object
intents = Intents.default()
intents.members = True # needed for $count

bot = commands.Bot(command_prefix=config["prefix"], help_command=PretenderHelpCommand(), intents=intents)
bot.config = config # for global cog access

# initialize the database
client = motor.AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_URI"))
bot.database = client.get_default_database("pretender")

# import all cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.statistics")
bot.load_extension("cogs.opting")
bot.load_extension("cogs.events")

# apply cooldowns to commands
apply_cooldowns(bot.config["Cooldowns"]["Durations"], bot.commands)

bot.run(os.getenv("DISCORD_TOKEN"))
