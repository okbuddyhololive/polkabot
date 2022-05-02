from discord.ext import commands
import toml
import os

with open("config.toml") as file:
    config = toml.load(file)

bot = commands.Bot(command_prefix=config["prefix"])
bot.config = config # for global cog access

# loading cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.events")
bot.load_extension("jishaku")

bot.run(os.getenv("DISCORD_TOKEN"))