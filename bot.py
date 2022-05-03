from discord.ext import commands
from discord import Intents
import toml

import logging
import os

from modules.webhooks import WebhookManager
from modules.chain import MessageManager

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

# for global cog access
bot.config = config
bot.messages = MessageManager.from_path(
    "data/messages.json",

    max_limit=bot.config["Chain"]["max_limit"],
    length=bot.config["Chain"]["length"],
    tries=bot.config["Chain"]["tries"]
)
bot.webhooks = WebhookManager.from_path("data/webhooks.json")

# loading cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.events")
bot.load_extension("jishaku")

bot.run(os.getenv("DISCORD_TOKEN"))