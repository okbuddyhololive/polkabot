from motor.motor_asyncio import AsyncIOMotorCollection
from discord.ext import commands, tasks
from discord import Message
import aiohttp

import logging
import random

from modules.chain import MessageManager

class Other(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager, blacklist: AsyncIOMotorCollection):
        self.bot = bot

        self.messages = messages
        self.blacklist = blacklist

        self.messages.max_limit = 50000

        self.images = []
        self.videos = []

        self.update_links.start()

    @commands.Cog.listener()
    async def on_message_delete(self, message: Message):
        if message.author != self.bot.user:
            return

        if not message.reference or not message.reference.resolved:
            return
        
        reply = message.reference.resolved
        prefix = self.bot.config["prefix"]

        if reply.content not in (prefix + "image", prefix + "video"):
            return
        
        await self.blacklist.insert_one({"url": message.content})

    @tasks.loop(hours=1)
    async def update_links(self):
        cursor = self.blacklist.find({})
        banned_links = [document["url"] for document in await cursor.to_list(length=None)]

        image_extensions = self.bot.config["Commands"]["Other"]["image_extensions"]
        video_extensions = self.bot.config["Commands"]["Other"]["video_extensions"]

        image_matches = await self.messages.links(image_extensions)
        video_matches = await self.messages.links(video_extensions)

        self.images = [message["url"]["match"] for message in image_matches if message["url"]["match"] not in banned_links]
        self.videos = [message["url"]["match"] for message in video_matches if message["url"]["match"] not in banned_links]

        logging.info(f"Updated links. Found {len(self.images)} images and {len(self.videos)} videos.")

    @commands.command()
    async def image(self, ctx: commands.Context):
        """
        Grabs a random image from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        if not self.images:
            return await ctx.message.reply("I didn't prepare the image links yet, please try again in a minute!", mention_author=False)

        async with ctx.typing():
            session = aiohttp.ClientSession()

            while True:
                link = random.choice(self.images)

                async with session.head(link) as response:
                    if response.status >= 400:
                        continue
                    else:
                        break

            await session.close()

        #await ctx.message.reply(f"Here's a random image for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

    @commands.command()
    async def video(self, ctx: commands.Context):
        """
        Grabs a random video from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        if not self.videos:
            return await ctx.message.reply("I didn't prepare the video links yet, please try again in a minute!", mention_author=False)

        async with ctx.typing():
            session = aiohttp.ClientSession()

            while True:
                link = random.choice(self.videos)

                async with session.head(link) as response:
                    if response.status >= 400:
                        continue
                    else:
                        break

            await session.close()

        #await ctx.message.reply(f"Here's a random video for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

    @commands.command()
    async def pot(self, ctx: commands.Context):
        """
        Sends an image of the leader of the Khmer Rouge.
        Meant to be invoked as an accident, when someone is talking about the history of Cambodia in the 70s.

        **Arguments:**
        None.
        """

        if random.randint(1, 100) <= 1:
            await ctx.message.reply("https://cdn.discordapp.com/attachments/963524275929747460/1125083804990701578/pot-stainless-steel.png", mention_author=True)
        else:
            await ctx.message.reply("https://cdn.discordapp.com/attachments/963524275929747460/1121226843446587402/fe3.png", mention_author=True)

def setup(bot: commands.Bot):
    bot.add_cog(Other(bot, 
        messages=MessageManager(bot.database, **bot.config["Chain"]),
        blacklist=bot.database.bannedLinks
    ))