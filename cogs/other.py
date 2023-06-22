from modules.chain import MessageManager
from discord.ext import commands
import aiohttp

import random

class Other(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager):
        self.bot = bot

        self.messages = messages
        self.messages.max_limit = 50000

        self.image_extensions = tuple(self.bot.config["Commands"]["Other"]["image_extensions"])
        #self.video_extensions = tuple(self.bot.config["Commands"]["Other"]["video_extensions"])

        self.pol_pot = self.bot.config["Commands"]["Other"]["pol_pot_image"]

    @commands.command()
    async def image(self, ctx: commands.Context):
        """
        Grabs a random image from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        await ctx.message.add_reaction("✅")

        async with ctx.typing():
            messages = await self.messages.default()

        messages = [message.get("content", "") for message in messages]
        messages = [message for message in messages if message.endswith(self.image_extensions)]

        session = aiohttp.ClientSession()

        while True:
            link = random.choice(messages)

            link = link[link.find("http"):]
            link = link.replace("media.discordapp.net", "cdn.discordapp.com")

            async with session.head(link) as response:
                if response.status == 404:
                    continue
                else:
                    break

        await session.close()
        
        #await ctx.message.reply(f"Here's a random image for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

    """
    @commands.command()
    async def video(self, ctx: commands.Context):
        '''
        Grabs a random video from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        '''

        async with ctx.typing():
            messages = await self.messages.default()

        messages = [message.get("content", "") for message in messages]
        messages = [message for message in messages if message.endswith(self.video_extensions)]

        link = random.choice(messages)

        link = link.split()[-1]
        link = link.replace("media.discordapp.net", "cdn.discordapp.com")

        await ctx.message.reply(f"Here's a random video for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
    """

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