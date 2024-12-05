import re
from typing import List, Optional

from discord import Colour, Embed, User
from discord.ext import commands

from modules.chain import MessageManager
from modules.cooldown import is_blacklisted

class Statistics(commands.Cog):
    def __init__(self, bot: commands.Bot, messages: MessageManager) -> None:
        self.bot = bot
        self.messages = messages

        with open(self.bot.config["Commands"]["User"]["stopwords_path"], "r", encoding="utf-8") as file:
            self.stopwords = [word.rstrip("\n") for word in file.readlines()]

        with open(self.bot.config["Commands"]["User"]["blacklist_path"], "r", encoding="utf-8") as file:
            self.censored = [word.rstrip("\n") for word in file.readlines()]

        self.pattern = re.compile(r"(https?:\/\/\S+)|(<a?:\w+:\d+>)", re.IGNORECASE)
        self.punctuation = (".", ",", "!", "?", ":", ";", "'", "\"", "(", ")", "[", "]", "{", "}", "-", "_", "+", "=", "/", "\\", "|", "<", ">", "@", "#", "$", "%", "^", "&", "*", "~", "`")

    # helper functions
    def remove_punctuation(self, word: str) -> str:
        result = word

        if result.startswith(self.punctuation):
            result = result[1:]

        if result.endswith(self.punctuation):
            result = result[:-1]

        return result

    def word_split(self, text: str) -> List[str]:
        if not text:
            return []

        content = text.strip()

        content = content.lower()
        words = content.split()

        filtered = []

        for word in words:
            if self.pattern.match(word):
                continue

            word = self.remove_punctuation(word)

            if word:
                filtered.append(word)

        return filtered

    # actual commands
    @commands.command()
    async def count(self, ctx: commands.Context, *, keyword: str):
        """
        Counts the amount of messages containing a keyword and shows the 10 people who've said it the most.
        Also includes the invoker, if they're in the top 10.

        **Arguments:**
        - `keyword`: The keyword to search for.
        """

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)
        else:
            await ctx.message.add_reaction("⏲️")

        messages = await self.messages.containing(keyword)

        keyword = keyword.lower()
        occurences = {}

        for message in messages:
            text = message.get("content")

            text = text.lower()
            author = message["author"]["id"]

            if author not in occurences:
                occurences[author] = 0

            occurences[author] += text.count(keyword)

        # sort the dictionary by name and then by count
        occurences = dict(sorted(occurences.items(), key=lambda occurence: occurence[0]))
        occurences = dict(sorted(occurences.items(), key=lambda occurence: occurence[1], reverse=True))

        embed = Embed(
            title=f"Top 10 users who've said \"{keyword}\":", 
            colour=Colour.blurple(),
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Invoked by @{ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        author_encountered = False
        index = 1

        for id, count in occurences.items():
            user = await self.bot.get_or_fetch_user(int(id))

            if not user:
                continue

            if any(word in user.name.lower() for word in self.censored):
                continue

            field_name = f"#{index} - @{user.name}"

            if user.id == ctx.author.id:
                field_name += " (You)"
                author_encountered = True

            embed.add_field(
                name=field_name,
                value=f"**{count}** uses",
            )

            if index == 10: # 10th place
                break

            index += 1

        if not author_encountered:
            leaderboard = list(occurences.keys())

            position = leaderboard.index(str(ctx.author.id)) + 1
            count = occurences[str(ctx.author.id)]

            embed.add_field(
                name=f"#{position} - @{ctx.author.name} (You)",
                value=f"**{count}** uses",
            )

        await ctx.message.remove_reaction("⏲️", ctx.me)
        await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command()
    async def top(self, ctx: commands.Context, target: Optional[User] = None):
        """
        Counts and shows the 10 most used words by a user.

        **Arguments:**
        - `target`: The user that will be analyzed.
        """

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)
        else:
            await ctx.message.add_reaction("⏲️")

        target = target or ctx.author
        occurences = {}

        messages = await self.messages.get(target)

        for message in messages:
            for word in self.word_split(message.get("content")):
                if word in self.stopwords + self.censored:
                    continue

                if word not in occurences:
                    occurences[word] = 0

                occurences[word] += 1

        occurences = dict(sorted(occurences.items(), key=lambda occurence: occurence[1], reverse=True))

        embed = Embed(
            title=f"Top 10 words said the most by {target.display_name}:", 
            colour=Colour.blurple(),
            timestamp=ctx.message.created_at
        )

        embed.set_footer(text=f"Invoked by @{ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=target.display_avatar.url)

        index = 1

        for word, count in occurences.items():
            embed.add_field(
                name=f"#{index} - \"{word}\"",
                value=f"**{count}** uses",
            )

            if index == 10: # 10th place
                break

            index += 1

        await ctx.message.remove_reaction("⏲️", ctx.me)
        await ctx.message.reply(embed=embed, mention_author=False)

    @commands.command()
    async def bottom(self, ctx: commands.Context, target: Optional[User] = None):
        """
        Counts and shows the 10 least used words by a user.

        **Arguments:**
        - `target`: The user that will be analyzed.
        """

        if is_blacklisted(ctx, self.bot.config["Blacklist"]):
            return await ctx.message.reply(self.bot.config["Blacklist"]["message"], mention_author=False)
        else:
            await ctx.message.add_reaction("⏲️")

        target = target or ctx.author
        occurences = {}

        messages = await self.messages.get(target)

        for message in messages:
            for word in self.word_split(message.get("content", "")):
                if word in self.stopwords + self.censored:
                    continue

                if word not in occurences:
                    occurences[word] = 0

                occurences[word] += 1

        occurences = dict(sorted(occurences.items(), key=lambda occurence: occurence[1]))

        embed = Embed(
            title=f"Top 10 words said the least by {target.display_name}:",
            colour=Colour.blurple(),
            timestamp=ctx.message.created_at
        )

        embed.set_footer(text=f"Invoked by @{ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=target.display_avatar.url)

        index = 1

        for word, count in occurences.items():
            embed.add_field(
                name=f"#{index} - \"{word}\"",
                value=f"**{count}** uses",
            )

            if index == 10: # 10th place
                break

            index += 1

        await ctx.message.remove_reaction("⏲️", ctx.me)
        await ctx.message.reply(embed=embed, mention_author=False)

def setup(bot: commands.Bot):
    bot.add_cog(Statistics(bot=bot, 
        messages=MessageManager(bot.database, **bot.config["Chain"])
    ))