from discord import Message, User
from discord import Embed, Colour
from discord.ext import commands

from motor.motor_asyncio import AsyncIOMotorCollection
import aiohttp

from typing import Optional

from modules.chain import MessageManager
from modules.webhooks import WebhookManager

class Impersonation(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager, webhooks: WebhookManager, blacklist: AsyncIOMotorCollection):
        self.bot = bot

        self.messages = messages
        self.webhooks = webhooks
        self.blacklist = blacklist

        with open(self.bot.config["Commands"]["User"]["blacklist_path"], "r", encoding="utf-8") as file:
            self.censored = [word.rstrip("\n") for word in file.readlines()]

    # helper functions
    def censor_bad_words(self, text: str) -> str:
        censored_text = text

        for word in self.censored:
            if word not in censored_text:
                continue

            censored_text = censored_text.replace(word, word[0] + ("*" * (len(word) - 2)) + word[-1])

        return censored_text

    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if not message.clean_content:
            return

        if message.channel.id in self.bot.config["Blacklist"]["channels"]:
            return

        if await self.blacklist.count_documents({"user": {"id": str(message.author.id)}}):
            return

        await self.messages.add(message)

    # actual commands here
    @commands.command()
    async def impersonate(self, ctx: commands.Context, victim: Optional[User] = None, *, content: Optional[str] = None):
        """
        Impersonates the invoker (or the person you specify), based on their messages that were collected.
        If the user has opted out of message collecting, it will be based on all messages in the database.
        The invoker can also specify a message to send, which will be used instead of the generated message.

        **Arguments:**
        - `victim`: The user to impersonate, is optional.
        - `content`: The message to send, is optional.
        """

        for role in getattr(ctx.author, "roles", []):
            if role.id not in self.bot.config["Blacklist"]["roles"]:
                continue

            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)

        if not content:
            await ctx.message.add_reaction("⏲️")

        session = aiohttp.ClientSession()

        victim = victim or ctx.author
        message = content or await self.messages.generate(victim)

        webhook = await self.webhooks.get(ctx.channel, session=session)

        if not content:
            await ctx.message.remove_reaction("⏲️", ctx.me)

        await ctx.message.delete()

        await webhook.send(self.censor_bad_words(message), username=victim.display_name, avatar_url=victim.display_avatar.url)
        await session.close()

    @commands.command(aliases=["leave", "bye"])
    async def fakekick(self, ctx: commands.Context, victim: Optional[User] = None):
        """
        Impersonates Saiki Koronbot, pretending the invoker (or the person the invoker specifies) has left the server,
        by sending a message into the channel where the command was invoked.

        **Arguments:**
        - `victim`: The targeted user, is optional.
        """

        victim = victim or ctx.author
        author = self.bot.get_user(self.bot.config["Commands"]["Fakekick"]["author"])

        if not author:
            author = await self.bot.fetch_user(self.bot.config["Commands"]["Fakekick"]["author"])

        session = aiohttp.ClientSession()
        webhook = await self.webhooks.get(ctx.channel, session=session)

        message = self.bot.config["Commands"]["Fakekick"]["content"]
        message = message.format(user=victim)

        await ctx.message.delete()

        await webhook.send(message, username=author.name, avatar_url=author.display_avatar.url)
        await session.close()

    @commands.command()
    async def gold(self, ctx: commands.Context):
        """
        Pretends to hide an invoker's message behind a paywall, sending an embed. 

        **Arguments:**
        None.
        """

        session = aiohttp.ClientSession()
        webhook = await self.webhooks.get(ctx.channel, session=session)

        message = self.bot.config["Commands"]["Gold"]["content"]
        message = message.format(guild=ctx.guild)

        colour = Colour.from_rgb(*self.bot.config["Commands"]["Gold"]["colour"])
        embed = Embed(description=message, colour=colour)

        await ctx.message.delete()

        await webhook.send(embed=embed, avatar_url=ctx.author.display_avatar.url, username=ctx.author.name)
        await session.close()

    @commands.command()
    async def delwebhook(self, ctx: commands.Context):
        await WebhookManager.remove(self.webhooks, ctx.channel)

def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(bot=bot,
        messages=MessageManager(bot.database, **bot.config["Chain"]), 
        webhooks=WebhookManager(bot.database),
        blacklist=bot.database.blacklist
    ))
