import logging
import random
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import parse_qs, urlparse

import aiohttp
from discord import Message
from discord.ext import commands, tasks
from motor.motor_asyncio import AsyncIOMotorCollection

from modules.chain import MessageManager
from modules.cooldown import is_blacklisted

class Other(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager, blacklist: AsyncIOMotorCollection) -> None:
        self.bot = bot

        self.messages = messages
        self.blacklist = blacklist

        self.messages.max_limit = 50000

        self.images = []
        self.videos = []

        self.update_links.start()

    # helper functions
    async def check_status_code(self, link: str) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(link, allow_redirects=True) as response:
                    return response.status < 400
            except aiohttp.ClientConnectorError:
                return False

    async def search_for_attachment(self, link: str) -> Optional[str]:
        url = urlparse(link)
        path = url.path.split("/")
        query = parse_qs(url.query)

        #print(url.netloc)
        #print(path)
        #print(query)

        if "ex" not in query or "is" not in query:
            return

        creation_date = datetime.fromtimestamp(int(query["is"][0], 16), tz=timezone.utc)
        expiration_date = datetime.fromtimestamp(int(query["ex"][0], 16), tz=timezone.utc)

        #print(creation_date)
        #print(expiration_date)

        if expiration_date > datetime.now(timezone.utc):
            return link

        channel_id = int(path[2])
        attachment_id = int(path[3])

        #print(channel_id)
        #print(attachment_id)

        channel = self.bot.get_channel(channel_id)

        if not channel:
            return

        async for message in channel.history(limit=101, around=creation_date, oldest_first=True):
            for attachment in message.attachments:
                if attachment.id == attachment_id:
                    return attachment.url

    # event listeners
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

    # tasks
    @tasks.loop(hours=1)
    async def update_links(self):
        cursor = self.blacklist.find({})
        banned_links = [document["url"] for document in await cursor.to_list(length=None)]

        image_extensions = tuple(self.bot.config["Commands"]["Other"]["image_extensions"])
        video_extensions = tuple(self.bot.config["Commands"]["Other"]["video_extensions"])

        matches = await self.messages.links(image_extensions + video_extensions)

        images = []
        videos = []

        for document in matches:
            link = document["url"]["match"]
            clean_link = link.rsplit("?", 1)[0]

            if link in banned_links or clean_link in banned_links:
                continue

            if clean_link.endswith(image_extensions):
                images.append(link)
            elif clean_link.endswith(video_extensions):
                videos.append(link)

        self.images = images
        self.videos = videos

        logging.info(f"Updated links. Found {len(self.images)} images and {len(self.videos)} videos.")

    # actual commands
    @commands.command()
    async def image(self, ctx: commands.Context):
        """
        Grabs a random image from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)

        if not self.images:
            return await ctx.message.reply("I didn't prepare the image links yet, please try again in a minute!", mention_author=False)

        async with ctx.typing():
            while True:
                link = random.choice(self.images)

                if link.startswith("https://cdn.discordapp.com/attachments/") or link.startswith("https://media.discordapp.net/attachments/"):
                    link = await self.search_for_attachment(link)

                    if not link:
                        continue
                elif not await self.check_status_code(link):
                    continue

                break

        #await ctx.message.reply(f"Here's a random image for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

    @commands.command()
    async def video(self, ctx: commands.Context):
        """
        Grabs a random video from the database and sends it in the channel where the command was invoked.

        **Arguments:**
        None.
        """

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)

        if not self.videos:
            return await ctx.message.reply("I didn't prepare the video links yet, please try again in a minute!", mention_author=False)

        async with ctx.typing():
            while True:
                link = random.choice(self.videos)

                if link.startswith("https://cdn.discordapp.com/attachments/") or link.startswith("https://media.discordapp.net/attachments/"):
                    link = await self.search_for_attachment(link)

                    if not link:
                        continue
                elif not await self.check_status_code(link):
                    continue

                break

        #await ctx.message.reply(f"Here's a random video for you! {link}\nIf it's not showing up an embed, it's most likely because it isn't available anymore.", mention_author=False)
        await ctx.message.reply(link, mention_author=False)

    @commands.command(hidden=True)
    async def pot(self, ctx: commands.Context):
        """
        Sends an image related to the Khmer Rouge.
        Meant to be invoked as an accident, when someone is talking about the history of Cambodia in the 70s.

        **Arguments:**
        None.
        """

        if random.randint(1, 100) <= 1:
            return await ctx.message.reply("https://cdn.discordapp.com/attachments/1313950286959611964/1313951187799900244/pot.jpg", mention_author=True)

        await ctx.message.reply(random.choice(self.bot.config["Commands"]["Other"]["pol_pot_images"]), mention_author=True)

    @commands.command("and", hidden=True)
    async def _and(self, ctx: commands.Context):
        """
        Sends a GIF related to Poland in a patriotic way.
        Meant to be invoked as an accident, when someone mistakenly adds a space between "pol" and "and".

        **Arguments:**
        None.
        """

        await ctx.message.reply(random.choice(self.bot.config["Commands"]["Other"]["pol_and_images"]), mention_author=True)

    @commands.command(hidden=True)
    async def error(self, ctx: commands.Context):
        raise SyntaxError(f"Congrats, @{ctx.author.name}! You found the exception handler test command!")

def setup(bot: commands.Bot):
    bot.add_cog(Other(bot=bot,
        messages=MessageManager(bot.database, **bot.config["Chain"]),
        blacklist=bot.database.bannedLinks
    ))