import discord
from discord import app_commands
from casinocore import GameMenu
import asyncio
import db
import config
import random
from core.plugins import Plugin
from core.helpers import isprivileged
from core.ui import LootboxUI, LOOTBOX_PRICE

class Fun(Plugin):
  def __init__(self, bot):
    self.bot = bot
    super().__init__(bot=bot)
    
  @app_commands.command(name = "coems",description = "Silly coems generator!")
  @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id,i.user.id))
  async def coems(self, interaction: discord.Interaction):
    item = db.items.get(interaction.user.id,1001)
    if item == 0:
      await interaction.response.send_message(f"You didn't buy this feature yet.\nSave up <:coins:1172819933093179443> ` 350 Coins ` and get it in the <#{config.SHOP_CHANNEL}>!",ephemeral=True)
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
  
  @app_commands.command(name = "casino", description = "Take a step into the casino luxury!")
  @app_commands.choices(mode=[app_commands.Choice(name="Public", value="false"),app_commands.Choice(name="Private", value="true")])
  @app_commands.describe(mode='Choose whether you want a Public or Private session. Public by default.')
  @app_commands.describe(bet='The amount you choose to bet. You can change this later.')
  async def casino(self, interaction: discord.Interaction, mode: app_commands.Choice[str] = None,bet: int = None):
    host_balance = db.get('economy','coins',interaction.user.id)
    if host_balance < 50:
      await interaction.response.send_message("You're too poor to take a step into the casino luxury. Save up at least <:coins:1172819933093179443>` 50 Coins ` to get started.",ephemeral=True)
      return
    if not bet:
      bet = 0
    else:
      if host_balance < bet:
        await interaction.response.send_message("You have insufficient funds.",ephemeral=True)
        return
      if bet not in range(50,1500):
        await interaction.response.send_message('Your Bet must be at least <:coins:1172819933093179443> ` 50 - 1500 Coins `',ephemeral=True)
        return
    host = interaction.user
    msg = '<:worldwide:1203760886842527855> ` Public `'
    key = None
    if mode:
      if mode.value == 'true':
        msg = '<:padlock:1178730730998734980> ` Private `'
        key = random.randint(1000,9999)
    embed = discord.Embed(title='<:poker:1176917180776992869> Casino Session',description=f"**Host:** {host.mention}\n**Lobby:** {msg}")
    await interaction.response.send_message(embed=embed,view=GameMenu(key,host.id,bet))

  @app_commands.command(name = "chatrevive",description = "Pings a role to revive the chat!")
  @app_commands.checks.cooldown(1, 1600, key=lambda i: (i.guild_id))
  async def chatrevive(self, interaction: discord.Interaction):
    item = db.items.get(interaction.user.id,1002)
    if item == 0:
      await interaction.response.send_message(f"You didn't buy this feature yet.\nSave up <:coins:1172819933093179443> ` 400 Coins ` and get it in the <#{config.SHOP_CHANNEL}>!",ephemeral=True)
    else:
      await interaction.response.send_message("Pinging the kittens...",ephemeral=True,delete_after=3)
      await interaction.channel.send(f"**{interaction.user.mention} Pinged <@&1139862719726624768>! :smile:**")

  @app_commands.command(name = "lootbox",description = "BETA | Take a risky action in hope of getting coins and items!")
  async def lootbox(self, interaction: discord.Interaction):
    if isprivileged(interaction.user):
      user_balance = db.get('economy', 'coins', interaction.user.id)
      if user_balance < 5:
        await interaction.response.send_message("You're too poor to open a lootbox. Save up at least <:coins:1172819933093179443> ` 5 Coins ` to get started.",ephemeral=True)
        return
      embed = discord.Embed(description=f"**How it works**\nYou can open lootboxes for how long you want.\nEach box costs <:coins:1172819933093179443> ` {LOOTBOX_PRICE} Coins `\nYou can get more coins, items, and even rare items!\n\n**But there's a catch:** There is a small chance that you will loose all your opened lootboxes and the coins you spent on them.\n\n**Are you ready?**")
      embed.set_author(name='Lootbox chain!',icon_url='https://cdn-icons-png.flaticon.com/512/8580/8580823.png'	)
      embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/8832/8832614.png')
      await interaction.response.send_message(embed=embed,view=LootboxUI(interaction.user))
    else:
      await interaction.response.send_message("You must be a Server Booster to use BETA features.",ephemeral=True)

  @app_commands.command(description = "BETA | Take a risky action in hope of getting coins and boosts!")
  async def slotmachine(self,interaction: discord.Interaction):
    await interaction.response.send_message("This feature is under development, stay tuned!",ephemeral=True)

async def setup(bot):
  await bot.add_cog(Fun(bot))