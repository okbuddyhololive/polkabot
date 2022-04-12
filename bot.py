from discord.ext import commands
import os

bot = commands.Bot(command_prefix="$") # TODO: make the prefix customizable in the config

# loading cogs
bot.load_extension("cogs.impersonation")
bot.load_extension("cogs.events")

bot.run(os.getenv("DISCORD_TOKEN"))