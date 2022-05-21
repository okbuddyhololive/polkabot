from discord.ext import commands
from discord import File

from io import StringIO
import traceback
import logging

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return

        exception = traceback.format_exception(type(error), error, error.__traceback__)

        message = (
            "Uh oh, I've ran into an issue while trying to execute this command!\n"
            "Please send the file below to the bot developers via DMs:\n"
        )
        
        stream = StringIO("".join(exception))
        file = File(stream, filename="error.log")
        
        await ctx.send(message, file=file)
        logging.warning(f"A user tried to use `${ctx.command}` but got an error: {error}")

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))