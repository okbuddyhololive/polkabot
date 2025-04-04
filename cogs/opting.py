from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorCollection

from modules.chain import MessageManager

class Opting(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager, blacklist: AsyncIOMotorCollection) -> None:
        self.bot = bot

        self.messages = messages
        self.blacklist = blacklist

    # opt in/out commands
    @commands.command()
    async def optin(self, ctx: commands.Context):
        """
        Opts into the message collection process, if the user is in the black list.

        **Arguments:**
        None.
        """

        document = {"user": {"id": str(ctx.author.id)}}

        if not await self.blacklist.count_documents(document):
            return await ctx.message.reply("You're already opted in!", mention_author=False)

        await self.blacklist.delete_one(document)
        await ctx.message.reply("You're now opted in!", mention_author=False)

    @commands.command()
    async def optout(self, ctx: commands.Context):
        """
        Opts out of the message collection process, if the user is not in the black list.
        Will ask for confirmation, in a form of a reaction to the bot message.

        **Arguments:**
        None.
        """

        document = {"user": {"id": str(ctx.author.id)}}

        if await self.blacklist.count_documents(document):
            return await ctx.message.reply("You're already opted out!", mention_author=False)

        message = await ctx.message.reply("Are you sure you want to opt out?\nReact with ✅ to confirm.", mention_author=False)
        await message.add_reaction("✅")

        try:
            await self.bot.wait_for("reaction_add",
                timeout=60.0,
                check=lambda reaction, user: user == ctx.author and str(reaction.emoji) == "✅"
            )
        except TimeoutError:
            return await message.edit(content="Didn't get a reaction in time, so you're still opted in.")

        await self.messages.remove(ctx.author)
        await self.blacklist.insert_one(document)

        await message.edit(content="Successfully deleted all message data from you and added you to the log blacklist!", mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Opting(bot=bot,
        messages=MessageManager(bot.database, **bot.config["Chain"]),
        blacklist=bot.database.optOutUsers
    ))