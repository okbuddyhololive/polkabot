from discord.ext.commands import cooldown as cooldown_decorator
from discord.ext.commands import Command, BucketType
from discord import utils

from typing import Set

def apply_cooldowns(cooldowns: dict, commands: Set[Command]):
    for name, value in cooldowns.items():
        cooldown = cooldown_decorator(rate=1, per=value, type=BucketType.user)
        command = utils.get(commands, name=name)

        cooldown(command)