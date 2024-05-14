from main import client
from discord.ext import commands

class Plugin(commands.Cog): 
    def __init__(self, bot: client):
        self.bot = bot
        
    
