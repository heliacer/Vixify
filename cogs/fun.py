import discord
from discord.ext import commands
from discord import app_commands
from gamecore import GameMenu
import asyncio
import random

#Change coemes role and chatrevive role to database items 

class Fun(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  @app_commands.command(name = "coems",description = "Aye pasta la bay be bean")
  @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id,i.user.id))
  async def coems(self, interaction: discord.Interaction):
    role = interaction.guild.get_role(1178726195467145256)
    if role not in interaction.user.roles:
      await interaction.response.send_message("You didn't buy this feature yet.\nSave up <:coins:1172819933093179443> ` 350 Coins ` and get it in the <#1142779979931856896>!",ephemeral=True)
      return
    await interaction.response.send_message("Generating coems :money_mouth:",ephemeral=True)
    messages = [
        "Aye pasta la bay be bean :smiling_face_with_3_hearts:",
        "Artim dada ba de men :money_mouth:",
        "Appkanim du na dunoo :sleeping:",
        "Ganganstyle de baylin..",
        "Muna mintip :money_mouth:",
        "Muna mintip :money_mouth:",
        "Muna mintip :money_mouth:",
        "Muna mintip :money_mouth:"
    ]
    for message in messages:
        await interaction.channel.send(message)
        await asyncio.sleep(1)
  
  @app_commands.command(name = "gamble", description = "Take risky action in the hope of getting coins")
  @app_commands.choices(mode=[app_commands.Choice(name="Public", value="false"),app_commands.Choice(name="Private", value="true")])
  @app_commands.describe(mode='Choose whether you want a Public or Private session. Public by default.')
  @app_commands.describe(bet='The amount you choose to bet. You can change this later.')
  async def gamble(self, interaction: discord.Interaction, mode: app_commands.Choice[str] = None,bet: int = None):
    if not bet:
      bet = 0
    host = interaction.user
    msg = '<:worldwide:1203760886842527855> ` Public `'
    key = None
    if mode:
      if mode.value == 'true':
        msg = '<:padlock:1178730730998734980> ` Private `'
        key = random.randint(1000,9999)
    embed = discord.Embed(title='<:poker:1176917180776992869> Gambling Session',description=f"**Host:** {host.mention}\n**Lobby:** {msg}")
    await interaction.response.send_message(embed=embed,view=GameMenu(key,host.id,bet))

  @app_commands.command(name = "chatrevive",description = "Pings a role to revive the chat!")
  @app_commands.checks.cooldown(1, 1600, key=lambda i: (i.guild_id))
  async def chatrevive(self, interaction: discord.Interaction):
    role = interaction.guild.get_role(1178726280959635616)
    if role:
      if role in interaction.user.roles:
        await interaction.response.send_message("Pinging the kittens...",ephemeral=True,delete_after=3)
        await interaction.channel.send(f"**{interaction.user.mention} Pinged <@&1139862719726624768>! :smile:**")
      else:
        await interaction.response.send_message("You didn't buy this feature yet.\nSave up <:coins:1172819933093179443> ` 400 Coins ` and get it in the <#1142779979931856896>!",ephemeral=True)
    else:
      await interaction.response.send_message("Role not found")

async def setup(bot):
  await bot.add_cog(Fun(bot))