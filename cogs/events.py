from discord.ext import commands
from discord import File

from io import StringIO
import traceback
import logging

from modules.cooldown import is_whitelisted

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.CommandOnCooldown):
            if is_whitelisted(ctx, self.bot.config["Cooldowns"]["Whitelist"]):
                return ctx.command.reset_cooldown(ctx)

            return await ctx.send(f"You're on cooldown, {ctx.author.mention}. Please try again in {round(error.retry_after, 2)} seconds.")

        if isinstance(error, commands.UserInputError):
            return await ctx.send(f"Oops, you didn't type the command correctly, {ctx.author.mention}.\nUse `{ctx.prefix}help {ctx.command.name}` for more information.")

        if isinstance(error, commands.NotOwner):
            return await ctx.send(f"This command is available only to the bot owners, {ctx.author.mention}.")

        exception = traceback.format_exception(type(error), error, error.__traceback__)

        message = (
            "Uh oh, I've ran into an issue while trying to execute this command!\n"
            "Please send the file below to the bot developers via DMs:\n"
        )

        stream = StringIO("".join(exception))
        file = File(stream, filename="error.log")

        await ctx.send(message, file=file)

        logging.warning(f"A user tried to use `{self.bot.command_prefix}{ctx.command}` but got an error: {error}")

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))