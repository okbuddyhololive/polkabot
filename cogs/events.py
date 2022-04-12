from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}!")

    # TODO: create an error handler

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))