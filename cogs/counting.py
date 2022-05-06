from discord.ext import commands
from discord import Embed, Colour
from datetime import datetime

class Counting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = self.bot.messages

    @commands.command()
    async def count(self, ctx: commands.Context, *, text: str):
        text = text.lower()
        occurences = {}
        messages = self.manager.messages

        for author, pack in messages.items():
            for message in pack:
                message = message.lower()

                if author not in occurences:
                    occurences[author] = 0
                
                occurences[author] += message.count(text)

        embed = Embed(
            title=f"Top 10 users who've typed '{text}':", 
            #description="(based on message data collected here thus far)",
            colour=Colour.blurple(),
            timestamp=datetime.utcnow()
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
    bot.add_cog(Counting(bot))