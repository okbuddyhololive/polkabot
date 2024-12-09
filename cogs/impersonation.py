from typing import Optional

import aiohttp
from discord import Colour, Embed, Message, NotFound, User
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorCollection

from modules.chain import MessageManager
from modules.cooldown import is_blacklisted
from modules.webhooks import WebhookManager

class Impersonation(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager, webhooks: WebhookManager, blacklist: AsyncIOMotorCollection) -> None:
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

            censored_text = censored_text.replace(word, word[0] + ("\\*" * (len(word) - 2)) + word[-1])

        return censored_text

    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if not message.clean_content and not message.attachments:
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

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)
        else:
            await ctx.message.add_reaction("⏲️")

        session = aiohttp.ClientSession()
        webhook = await self.webhooks.get(ctx.channel, session=session)

        victim = victim or ctx.author        

        if not content:
            dataset = await self.messages.get(victim)

            if not dataset or len(dataset) < self.messages.min_limit:
                dataset = await self.messages.default()

            message = await self.messages.generate(dataset)
        else:
            message = content

        await ctx.message.remove_reaction("⏲️", ctx.me)
        await ctx.message.delete()

        await webhook.send(self.censor_bad_words(message), username=victim.display_name, avatar_url=victim.display_avatar.url)
        await session.close()

    @commands.command()
    async def echo(self, ctx: commands.Context, *, text: str):
        """
        Generates a message containing the specified text by the invoker, based on the messages from the database.

        **Arguments:**
        - `text`: The text that the generated message will contain.
        """

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)
        else:
            await ctx.message.add_reaction("⏲️")

        dataset = await self.messages.containing(text)

        if not dataset or len(dataset) < self.messages.min_limit:
            return await ctx.message.reply("I couldn't find any messages containing that text.", mention_author=False)

        while True:
            message = await self.messages.generate(dataset)

            if text in message:
                break

        await ctx.message.remove_reaction("⏲️", ctx.me)
        await ctx.message.reply(self.censor_bad_words(message), mention_author=False)

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

        if not webhook:
            webhook = await self.webhooks.create(ctx.channel)

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

        if not webhook:
            webhook = await self.webhooks.create(ctx.channel)

        message = self.bot.config["Commands"]["Gold"]["content"]
        message = message.format(guild=ctx.guild)

        colour = Colour.from_rgb(*self.bot.config["Commands"]["Gold"]["colour"])
        embed = Embed(description=message, colour=colour)

        await ctx.message.delete()

        await webhook.send(embed=embed, avatar_url=ctx.author.display_avatar.url, username=ctx.author.name)
        await session.close()

    @commands.command(hidden=True, aliases=["delwebhook"])
    @commands.is_owner()
    async def delhook(self, ctx: commands.Context):
        """
        Deletes a webhook made by the bot inside the channel where the command is being executed.
        Only available to the bot owners.

        **Arguments:**
        None.
        """

        session = aiohttp.ClientSession()
        webhook = await self.webhooks.get(ctx.channel, session=session)

        if not webhook:
            return await ctx.message.reply("There is no webhook in this channel.")

        try:
            await webhook.delete()
        except NotFound:
            pass

        await self.webhooks.remove(ctx.channel)

        await ctx.message.reply("Webhook deleted successfully.")
        await session.close()

def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(bot=bot,
        messages=MessageManager(bot.database, **bot.config["Chain"]), 
        webhooks=WebhookManager(bot.database),
        blacklist=bot.database.blacklist
    ))
