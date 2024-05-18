import discord
from discord.ext import commands

def isauthor(message: discord.Message, member: discord.Member):
    return message.author == member


