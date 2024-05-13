import discord
from discord.ext import commands
import config

def is_author(message: discord.Message, member: discord.Member):
    return message.author == member

def has_admin():
    def predicate(ctx: commands.Context):
        return ctx.message.author.guild_permissions.administrator
    return commands.check(predicate)

def isme():
    async def predicate(ctx):
        return ctx.author.id in config.ADMIN
    return commands.check(predicate)