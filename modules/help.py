from discord.ext import commands
from discord import Embed, Colour

class PretenderHelpCommand(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping: dict):
        ctx = self.context

        embed = Embed(colour=Colour.blurple())
        embed.description = (
            f"Use `{self.clean_prefix}help [command]` for more info on a command.\n"
            f"You can also use `{self.clean_prefix}help [category]` for more info on a category.\n\n"
        )

        for cog, commands in mapping.items():
            signatures = " ".join(command.name for command in commands)

            if not signatures:
                continue
            
            name = cog.qualified_name if cog is not None else "Uncategorized"

            if name == "Jishaku": # hide jishaku commands
                continue
            
            embed.description += f"__**{name}**__\n{signatures}\n"

        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at

        await ctx.message.reply(embed=embed, mention_author=False)

    async def send_cog_help(self, cog: commands.Cog):
        ctx = self.context

        embed = Embed(colour=Colour.blurple())
        embed.description = (
            f"Use `{self.clean_prefix}help [command]` for more info on a command.\n"
            f"You can also use `{self.clean_prefix}help [category]` for more info on a category.\n\n"
        )

        name = cog.qualified_name if cog is not None else "Uncategorized"
        embed.description += f"**{name} Commands**\n"
        
        for command in cog.get_commands():
            embed.description += f"`{self.get_command_signature(command)}`\n"

        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at

        await ctx.message.reply(embed=embed, mention_author=False)

    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        
        embed = Embed(
            title=f"`{self.get_command_signature(command)}`\n",
            description=command.help,
            colour=Colour.blurple()
        )

        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at

        await ctx.message.reply(embed=embed, mention_author=False)

    async def command_not_found(self, string: str) -> Embed:
        ctx = self.context

        embed = Embed(description=f"No command/category called `{string}` found!", colour=Colour.red())
        embed.set_footer(text=f"Invoked by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at

        #await ctx.message.reply(embed=embed, mention_author=False)
        return embed
    
    async def send_error_message(self, error: Embed):
        await self.context.message.reply(embed=error, mention_author=False)