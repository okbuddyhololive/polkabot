from discord.ext import commands, tasks
from discord import Message, AsyncWebhookAdapter
import aiohttp

import json
import os

class Impersonation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.messages = self.bot.messages
        self.webhooks = self.bot.webhooks
        self.blacklist = self._load_blacklist()

        self.dump_data.start()
    
    def _load_blacklist(self):
        path = "data/blacklist.json"

        if not os.path.exists(path):
            with open(path, "w") as file:
                file.write("[]")
        
        with open(path, "r") as file:
            return json.load(file)
    
    # tasks for dumping message & webhook data, in case of a bot shutdown
    @tasks.loop(seconds=60)
    async def dump_data(self):
        self.messages.to_path("data/messages.json")
        self.webhooks.to_path("data/webhooks.json")

        with open("data/blacklist.json", "w") as file:
            json.dump(self.blacklist, file)

    # events for interacting with webhook/message data
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
 
        if message.author.id in self.blacklist:
            return
        
        await self.messages.add(message)
    # adding this so i can be sure it saves the session lol
    # actual commands here
    @commands.command()
    async def impersonate(self, ctx: commands.Context):
        session = aiohttp.ClientSession()

        message = await self.messages.generate(ctx.author)
        webhook = await self.webhooks.get(ctx.channel, AsyncWebhookAdapter(session))

        await ctx.message.delete()
        await webhook.send(message, username=ctx.author.name, avatar_url=ctx.author.avatar_url)
        await session.close()
    
    # opt in/out commands
    @commands.command()
    async def optin(self, ctx: commands.Context):
        if ctx.author.id not in self.blacklist:
            return await ctx.message.reply("You're already opted in!", mention_author=False)
        
        self.blacklist.remove(ctx.author.id)
        await ctx.message.reply("You're now opted in!", mention_author=False)

    @commands.command()
    async def optout(self, ctx: commands.Context):
        if ctx.author.id in self.blacklist:
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
        self.blacklist.append(ctx.author.id)

        await message.edit(content="Successfully deleted all message data from you and added you to the log blacklist!", mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Impersonation(bot))