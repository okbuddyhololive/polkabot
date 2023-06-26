from modules.chain import MessageManager
from discord.ext import commands
import aiohttp

import random

class Other(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager):
        self.bot = bot

        self.messages = messages
        self.messages.max_limit = 50000

        self.image_extensions = self.bot.config["Commands"]["Other"]["image_extensions"]
        self.video_extensions = self.bot.config["Commands"]["Other"]["video_extensions"]

        self.pol_pot = self.bot.config["Commands"]["Other"]["pol_pot_image"]

    @commands.command()
    async def image(self, ctx: commands.Context):
        """
        Grabs a random image from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        await ctx.message.add_reaction("⏲️")

        async with ctx.typing():
            messages = await self.messages.links(self.image_extensions)

        messages = [message["url"]["match"] for message in messages]
        session = aiohttp.ClientSession()

        while True:
            link = random.choice(messages)
            link = link.replace("media.discordapp.net", "cdn.discordapp.com")

            async with session.head(link) as response:
                if response.status >= 400:
                    continue
                else:
                    break

        await session.close()
        await ctx.message.remove_reaction("⏲️", ctx.me)

        #await ctx.message.reply(f"Here's a random image for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

    @commands.command()
    async def video(self, ctx: commands.Context):
        """
        Grabs a random video from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        await ctx.message.add_reaction("⏲️")

        async with ctx.typing():
            messages = await self.messages.links(self.video_extensions)

        messages = [message["url"]["match"] for message in messages]
        session = aiohttp.ClientSession()

        while True:
            link = random.choice(messages)
            link = link.replace("media.discordapp.net", "cdn.discordapp.com")

            async with session.head(link) as response:
                if response.status >= 400:
                    continue
                else:
                    break

        await session.close()
        await ctx.message.remove_reaction("⏲️", ctx.me)

        #await ctx.message.reply(f"Here's a random image for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

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