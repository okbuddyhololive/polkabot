from discord.ext.commands import cooldown as cooldown_decorator
from discord.ext.commands import Command, BucketType, Context
from discord import utils

from typing import Set

def apply_cooldowns(cooldowns: dict, commands: Set[Command]):
    for name, value in cooldowns.items():
        cooldown_decorator(rate=1, per=value, type=BucketType.channel)(utils.get(commands, name=name))

def is_whitelisted(ctx: Context, whitelists: dict) -> bool:
    if ctx.author.id in whitelists["users"]:
        return True

    if ctx.message.channel.id in whitelists["channels"]:
        return True

    for role in ctx.author.roles:
        if role.id in whitelists["roles"]:
            return True

    return False