from discord.ext import commands
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

        logging.warning(f"A user tried to use `${ctx.command}` but got an error: {error}")

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))