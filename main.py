import asyncio
import os
import io
import random
import config
import traceback
import db
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()  # Enable all intents
client = commands.Bot(
  command_prefix="?",
  intents=intents,
)


@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')
  await client.tree.sync()
  print("synced slash command tree")
  db.refresh(client.get_guild(config.GUILD).member_count*200,client.user.id)
  await client.change_presence(activity = discord.Activity(type = discord.ActivityType.custom,name = " ",state = 'Keep your eyes on the prize!'))

     
@client.command()
async def ping(ctx):
  msg = await ctx.send('Pong!')
  await msg.edit(content='Pong! ``{0}ms``'.format(round(client.latency, 1))) 

@client.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
  if isinstance(error, commands.CommandOnCooldown):
    CooldownEmbed = discord.Embed(description=f'***<:sandclock:1203261564291911680> This command is on cooldown. Try again in {error.retry_after:.2f} seconds.***')
    await ctx.send(CooldownEmbed,ephemeral=True)
  elif isinstance(error,commands.errors.MissingRequiredArgument):
    await ctx.reply(f'<:progresschart:1178590023759695952> {error}')
  elif isinstance(error, (commands.CheckFailure, commands.CommandNotFound)):
      pass
  else:
    traceback.print_exception(error)
    exception = traceback.format_exception(error)
    file = discord.File(filename="error.log", fp=io.BytesIO(''.join(exception).encode()))
    ErrorEmbed = discord.Embed(description=f'***<:err:1203262608929722480> There was an unhandled Internal Error. Please try again later.***')
    ErrorEmbed.set_footer(text=error)
    await ctx.send(embed=ErrorEmbed,file=file)

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
  if isinstance(error, app_commands.CommandOnCooldown):
    CooldownEmbed = discord.Embed(description=f'***<:sandclock:1203261564291911680> This command is on cooldown. Try again in {error.retry_after:.2f} seconds.***')
    await interaction.response.send_message(embed=CooldownEmbed,ephemeral=True)
  else:
    traceback.print_exception(error)
    exception = traceback.format_exception(error)
    file = discord.File(filename="error.log", fp=io.BytesIO(exception.encode()))
    ErrorEmbed = discord.Embed(description=f'***<:err:1203262608929722480> There was an unhandled Internal Error. Please try again later.***')
    ErrorEmbed.set_footer(text=error)
    await interaction.response.send_message(embed=ErrorEmbed,file=file)


cogsList = []
for file in os.listdir('cogs'):
  if file.endswith('.py'):
    cogsList.append(
      f'cogs.{file[:-3]}'
    )

async def load():
  for cog in cogsList:
    await client.load_extension(cog)

try:
  asyncio.run(load())
except:
  traceback.print_exc()

load_dotenv()
client.run(os.getenv('TOKEN'))