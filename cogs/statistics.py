from discord.ext import commands
from discord import Embed, Colour, User
from discord import NotFound

from typing import Union, Optional, List

from modules.chain import MessageManager

class Statistics(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager):
        self.bot = bot
        self.messages = messages

    # helper functions
    def word_split(self, text: str) -> List[str]:
        content = text.lower()

        return content.split()
    
    # actual commands
    @commands.command()
    async def count(self, ctx: commands.Context, *, content: Union[User, str]):
        """
        Counts the amount of messages containing a keyword and shows the Top #10 people who said it.

        **Arguments:**
        - `keyword`: The keyword to search for.
        """

        if isinstance(content, str):
            keyword = content.lower()
        else:
            keyword = f"@{content.name}"
        
        occurences = {}

        async with ctx.typing():
            messages = await self.messages.containing(keyword)

        for message in messages:
            text = message.get("content")
            text = text.lower()
            
            author = message["author"]["id"]
            
            if author not in occurences:
                occurences[author] = 0
                
            occurences[author] += text.count(keyword)
        
        # sorting it by the most number of occurences
        occurences = dict(sorted(occurences.items(), key=lambda occurence: occurence[1], reverse=True))

        embed = Embed(
            title=f"Top #10 users who've said \"{keyword}\":", 
            colour=Colour.blurple(),
            timestamp=ctx.message.created_at
        )

        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)
        index = 1

        for id, count in occurences.items():
            user = self.bot.get_user(int(id))

            if not user:
                try:
                    user = await self.bot.fetch_user(int(id))
                except NotFound:
                    continue
            
            embed.add_field(
                name=f"#{index} - {str(user)}",
                value=f"**{count}** uses",
            )

            if index == 10: # 10th place
                break
            
            index += 1
        
        await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command()
    async def user(self, ctx: commands.Context, target: Optional[User] = None):
        target = target or ctx.author
        occurences = {}

        async with ctx.typing():
            messages = await self.messages.get(target)

        for message in messages:
            for word in self.word_split(message.get("content", "")):
                if word not in occurences:
                    occurences[word] = 0

                occurences[word] += 1
        
        occurences = dict(sorted(occurences.items(), key=lambda occurence: occurence[1], reverse=True))

        embed = Embed(
            title=f"Top #10 words said by {target.display_name}:", 
            colour=Colour.blurple(),
            timestamp=ctx.message.created_at
        )

        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)
        #embed.set_thumbnail(url=target.avatar_url)

        index = 1

        for word, count in occurences.items():
            embed.add_field(
                name=f"#{index} - \"{word}\"",
                value=f"**{count}** uses",
            )

            if index == 10: # 10th place
                break

            index += 1
        
        await ctx.message.reply(embed=embed, mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Statistics(bot=bot, 
        messages=MessageManager(bot.database, **bot.config["Chain"])
    ))