import asyncio
import os
import random
import config
import traceback
from dbmanager import check_reset
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.all()  # Enable all intents
client = commands.Bot(
  command_prefix="?",
  intents=intents,
)

statuses = ["Starting a inflation...","Gathering Coems...","Stealing some coins...","Breaking in a bank...","Going on a rampage..."]
async def status():
    while True:
        await client.change_presence(activity = discord.Activity(type = discord.ActivityType.custom,name = " ",state = random.choice(statuses)))
        await asyncio.sleep(10)

@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')
  await client.tree.sync()
  print("synced slash command tree")
  check_reset(client.get_guild(config.guild).member_count*500,client.user.id)
  client.loop.create_task(status())
     
@client.command()
async def ping(ctx):
  msg = await ctx.send('Pong!')
  await msg.edit(content='Pong! ``{0}ms``'.format(round(client.latency, 1))) 


@client.event
async def on_command_error(ctx, error: commands.CommandError):
  if isinstance(error, commands.CommandOnCooldown):
    CooldownEmbed = discord.Embed(description=f'***<:sandclock:1203261564291911680> This command is on cooldown. Try again in {error.retry_after:.2f} seconds.***')
    await ctx.send(CooldownEmbed,ephemeral=True)
  elif isinstance(error,commands.CheckFailure):
    pass
  elif isinstance(error,commands.CommandNotFound):
    pass
  else:
    traceback.print_exception(error)
    exception = traceback.format_exception(error)
    ErrorEmbed = discord.Embed(description=f'***<:err:1203262608929722480> There was an Internal Error. Please try again later.***\n\n```fix\n{"".join(exception)}\n```')
    await ctx.send(embed=ErrorEmbed)

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
  if isinstance(error, app_commands.CommandOnCooldown):
    CooldownEmbed = discord.Embed(description=f'***<:sandclock:1203261564291911680> This command is on cooldown. Try again in {error.retry_after:.2f} seconds.***')
    await interaction.response.send_message(embed=CooldownEmbed,ephemeral=True)
  else:
    traceback.print_exception(error)
    exception = traceback.format_exception(error)
    ErrorEmbed = discord.Embed(description=f'***<:err:1203262608929722480> There was an Internal Error. Please try again later.***\n\n```fix\n{"".join(exception)}\n```')
    await interaction.response.send_message(embed=ErrorEmbed)

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
client.run(config.bot_token)