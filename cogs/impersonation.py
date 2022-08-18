from discord import Message, User, AsyncWebhookAdapter
from discord.ext import commands
import aiohttp

from typing import Optional

from modules.chain import MessageManager
from modules.webhooks import WebhookManager

class Impersonation(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager, webhooks: WebhookManager):
        self.bot = bot

        self.messages = messages
        self.webhooks = webhooks
    
    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        
        if not message.clean_content:
            return
        
        if message.channel.id in self.bot.config["blacklist"]:
            return
        
        if await self.blacklist.count_documents({"user": {"id": str(message.author.id)}}):
            return
        
        await self.messages.add(message)
    
    # actual commands here
    @commands.command()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def impersonate(self, ctx: commands.Context, victim: Optional[User] = None):
        """
        Impersonates the invoker (or the person you specify), based on their messages that were collected.
        If the user has opted out of message collecting, it will be based on all messages in the database.

        **Arguments:**
        - `victim`: The user to impersonate, is optional.
        """

        session = aiohttp.ClientSession()
        victim = victim or ctx.author

        message = await self.messages.generate(victim)
        webhook = await self.webhooks.get(ctx.channel, AsyncWebhookAdapter(session))

        await ctx.message.delete()
        await webhook.send(message, username=victim.name, avatar_url=victim.avatar_url)
        await session.close()

def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(bot=bot,
        messages=MessageManager(bot.database, **bot.config["Chain"]), 
        webhooks=WebhookManager(bot.database)
    ))