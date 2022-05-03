from discord.ext import commands, tasks
from discord import Message, AsyncWebhookAdapter
import aiohttp

class Impersonation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.messages = self.bot.messages
        self.webhooks = self.bot.webhooks

        self.dump_webhooks.start()
        self.dump_messages.start()
    
    # tasks for dumping message & webhook data, in case of a bot shutdown
    @tasks.loop(seconds=60)
    async def dump_webhooks(self):
        self.webhooks.to_path("data/webhooks.json")

    @tasks.loop(seconds=60)
    async def dump_messages(self):
        self.messages.to_path("data/messages.json")
    
    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return
        
        if message.webhook_id is not None:
            return
        
        # TODO: add some if-checks here if we do "opt in/out" stuff
        await self.messages.add(message)
    
    # actual commands here
    @commands.command()
    async def impersonate(self, ctx):
        session = aiohttp.ClientSession()

        message = await self.messages.generate(ctx.author)
        webhook = await self.webhooks.get(ctx.channel, AsyncWebhookAdapter(session))

        await ctx.message.delete()
        await webhook.send(message, username=ctx.author.name, avatar_url=ctx.author.avatar_url)
        await session.close()
    
def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(bot))