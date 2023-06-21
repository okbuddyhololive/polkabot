from discord.ext import commands

from modules.chain import MessageManager

class Other(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager):
        self.bot = bot

        self.messages = messages
        self.pol_pot = self.bot.config["Commands"]["Other"]["pol_pot_image"]

    @commands.command()
    async def pot(self, ctx: commands.Context):
        """
        Sends an image of the leader of the Khmer Rouge.
        Meant to be invoked as an accident, when someone is talking about the history of Cambodia in the 70s.

        **Arguments:**
        None.
        """

        await ctx.message.reply(self.pol_pot, mention_author=True)

def setup(bot: commands.Bot):
    bot.add_cog(Other(bot, 
        messages=MessageManager(bot.database, **bot.config["Chain"])
    ))