import sys
sys.dont_write_bytecode = True
import discord
from discord.ext import commands
import os
import asyncio
import dotenv
import config
import db

dotenv.load_dotenv()

TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()

class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=intents)

    async def on_ready(self):
        await self.tree.sync()
        print(f'I have logged in as {self.user.name} | {len(self.all_commands)} Commands have been synced')
        db.refresh(client.get_guild(config.GUILD).member_count*200,client.user.id)

client = Client()

async def run():
    for root, dirs, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py'):
                relative_path = os.path.relpath(os.path.join(root, filename), './')
                extension_name = os.path.splitext(relative_path)[0].replace(os.sep, '.')
                await client.load_extension(extension_name)
                
if __name__ == '__main__':
    asyncio.run(run())
    client.run(TOKEN)
    
