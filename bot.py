import logging
import os
import tomllib

import dotenv
import motor.motor_asyncio as motor
from discord import Intents
from discord.ext import commands

from modules.cooldown import apply_cooldowns
from modules.help import PretenderHelpCommand

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
    config = tomllib.load(file)

# create the bot object
intents = Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config["prefix"], help_command=PretenderHelpCommand(), intents=intents)
bot.config = config

# initialize the database
client = motor.AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_URI"))
bot.database = client.get_default_database("pretender")

# import all cogs
for name in os.listdir("cogs"):
    if name.endswith(".py"):
        bot.load_extension(f"cogs.{name[:-3]}")

# apply cooldowns to commands
apply_cooldowns(bot.config["Cooldowns"]["Durations"], bot.commands)

# run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
