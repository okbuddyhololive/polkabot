from discord.ext import commands, tasks
from discord import Message, AsyncWebhookAdapter
import aiohttp

import json

class Impersonation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.messages = self.bot.messages
        self.webhooks = self.bot.webhooks
        self.blacklist = self._load_blacklist()

        self.dump_data.start()
    
    def _load_blacklist(self):
        with open("data/blacklist.json", "r") as file:
            return json.load(file)
    
    # tasks for dumping message & webhook data, in case of a bot shutdown
    @tasks.loop(seconds=60)
    async def dump_data(self):
        self.messages.to_path("data/messages.json")
        self.webhooks.to_path("data/webhooks.json")

        with open("data/blacklist.json", "w") as file:
            json.dump(self.blacklist, file, indent=4)

    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
 
        if message.author.id in self.blacklist:
            return
        
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
    
    @commands.command()
    async def optout(self, ctx):
        await self.messages.remove(ctx.author)
        self.blacklist.append(ctx.author.id)
        await ctx.message.reply("Successfully deleted all message data from you and added you to the log blacklist!", mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(bot))