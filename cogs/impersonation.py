from discord import Message, User, AsyncWebhookAdapter
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
    
    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
 
        #if message.author.id in self.blacklist:
        #    return
        
        await self.messages.add(message)
    
    # actual commands here
    @commands.command()
    async def impersonate(self, ctx: commands.Context, victim: Optional[User]):
        session = aiohttp.ClientSession()
        victim = victim or ctx.author

        message = await self.messages.generate(victim)
        webhook = await self.webhooks.get(ctx.channel, AsyncWebhookAdapter(session))

        await ctx.message.delete()
        await webhook.send(message, username=ctx.author.name, avatar_url=ctx.author.avatar_url)
        await session.close()
    
    # opt in/out commands
    @commands.command()
    async def optin(self, ctx: commands.Context):
        entry = await self.blacklist.find_one({"user": {"id": ctx.author.id}})

        if not entry:
            return await ctx.message.reply("You're already opted in!", mention_author=False)
        
        await self.blacklist.delete_one(entry)
        await ctx.message.reply("You're now opted in!", mention_author=False)

    @commands.command()
    async def optout(self, ctx: commands.Context):
        entry = await self.blacklist.find_one({"user": {"id": ctx.author.id}})
        if entry:
            return await ctx.message.reply("You're already opted out!", mention_author=False)
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅"
        
        message = await ctx.message.reply("Are you sure you want to opt out?\nReact with ✅ to confirm.", mention_author=False)
        await message.add_reaction("✅")

        try:
            await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except TimeoutError:
            return await message.edit(content="Didn't get a reaction in time, so you're still opted in.")
        
        await self.messages.remove(ctx.author)
        await self.blacklist.insert_one({"user": {"id": ctx.author.id}})

        await message.edit(content="Successfully deleted all message data from you and added you to the log blacklist!", mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(
        bot=bot,

        messages=MessageManager(bot.database, **bot.config["Chain"]), 
        webhooks=WebhookManager(bot.database),
        blacklist=bot.database.blacklist
    ))