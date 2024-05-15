from main import Client
from discord.ext import commands

class Plugin(commands.Cog): 
    def __init__(self, bot: Client):
        self.bot = bot
        
    
