from discord.ext import commands
from discord import Embed, Colour

from modules.chain import MessageManager

class Counting(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager):
        self.bot = bot
        self.messages = messages

    @commands.command()
    async def count(self, ctx: commands.Context, *, keyword: str):
        """
        Counts the amount of messages containing a keyword and shows the Top #10 people who said it.

        **Arguments:**
        - `keyword`: The keyword to search for.
        """

        keyword = keyword.lower()
        occurences = {}
        messages = await self.messages.containing(keyword)

        for message in messages:
            text = message.get("content")
            text = text.lower()
            author = message["author"]["id"]
            
            if author not in occurences:
                occurences[author] = 0
                
            occurences[author] += text.count(keyword)

        embed = Embed(
            title=f"Top 10 users who've typed '{keyword}':", 
            #description="(based on message data collected here thus far)",
            colour=Colour.blurple(),
            timestamp=ctx.message.created_at
        )

        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)

        for index, (id, count) in enumerate(occurences.items()):
            user = self.bot.get_user(int(id))

            embed.add_field(
                name=f"#{index + 1} - {str(user)}",
                value=f"**{count}** uses",
            )
        
        await ctx.message.reply(embed=embed, mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Counting(bot=bot, messages=MessageManager(bot.database, **bot.config["Chain"])))