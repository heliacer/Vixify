import discord
from discord import ui
from discord.ext import commands
from discord import app_commands
from casinocore import GameMenu
import asyncio
import db
import config
import random
from core.plugins import Plugin
from core.helpers import winchance

class LootboxUI(ui.View):
  def __init__(self,next=True,coins_value=5,total_spent=0,index=1,total_rewards=[]):
    super().__init__()
    self.index: int = index
    self.coins_value: int = coins_value
    self.total_spent: int = total_spent
    self.total_rewards: list = total_rewards
    if next:
      label = f'Open next for {self.coins_value} Coins' if self.coins_value > 5 else 'Open lootbox for 5 Coins'
      openButton = ui.Button(label=label, emoji='<:checkout:1175007951669436446>', style=discord.ButtonStyle.primary)
      openButton.callback = self.open
      self.add_item(openButton)
    if self.coins_value > 5:
      claimButton = ui.Button(label='Claim All', emoji='<:features:1178989659976642581>', style=discord.ButtonStyle.gray)
      claimButton.callback = self.claim
      self.add_item(claimButton)

  async def open(self, interaction: discord.Interaction):
    print(f"Coins value: {self.coins_value}\nTotal spent: {self.total_spent}\nIndex: {self.index}")
    user_balance = db.get('economy', 'coins', interaction.user.id)
    embed1 = discord.Embed(description='<a:loading:1239608763447640114> ***Opening lootbox...***', color=discord.Color.blurple())
    await interaction.response.edit_message(embed=embed1, view=None)
    await asyncio.sleep(1)
    embed2 = discord.Embed()
    db.exchange(interaction.client.user.id,interaction.user.id, self.coins_value)
    self.coins_value += 5
    self.total_spent += self.coins_value
    if winchance(80):
      rewards = ['undefined', 'still need to implement this part', 'but you get the idea']
      self.total_rewards.extend(rewards)
      embed2.description = f"**You opened a lootbox and found:**\n- {'\n- '.join([item for item in rewards])}"
      embed2.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/7839/7839136.png')
      if user_balance < self.coins_value + 5:
          embed2.description += f'\nAnd you spent all your money! No more lootboxes for you!'
          self.setday(interaction.user.id)
      await interaction.edit_original_response(embed=embed2,view=LootboxUI(
        next=user_balance > self.coins_value + 5,
        coins_value=self.coins_value,
        total_spent=self.total_spent,
        index=self.index,
        total_rewards=self.total_rewards
        ))
      self.index += 1
    else:
      self.setday(interaction.user.id)
      embed2.description = f'**You opened a Lootbox and found nothing!**\n\nYou lost all your opened lootboxes and <:coins:1172819933093179443> ` {self.total_spent} Coins `!'
      embed2.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/3741/3741593.png')
      await interaction.edit_original_response(embed=embed2, view=None)

  def claim(self, interaction: discord.Interaction):
    # TODO : implement claiming lootbox rewards
    pass

  def setday(self, user_id: int):
    pass
    # TODO : implement daily lootbox limit

  

class Fun(Plugin):
  def __init__(self, bot):
    self.bot = bot
    super().__init__(bot=bot)
    
  @app_commands.command(name = "coems",description = "Silly coems generator!")
  @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id,i.user.id))
  async def coems(self, interaction: discord.Interaction):
    role = interaction.guild.get_role(1178726195467145256)
    if role not in interaction.user.roles:
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
    role = interaction.guild.get_role(1178726280959635616)
    if role:
      if role in interaction.user.roles:
        await interaction.response.send_message("Pinging the kittens...",ephemeral=True,delete_after=3)
        await interaction.channel.send(f"**{interaction.user.mention} Pinged <@&1139862719726624768>! :smile:**")
      else:
        await interaction.response.send_message(f"You didn't buy this feature yet.\nSave up <:coins:1172819933093179443> ` 400 Coins ` and get it in the <#{config.SHOP_CHANNEL}>!",ephemeral=True)
    else:
      await interaction.response.send_message("Role not found")

  @app_commands.command(name = "lootbox",description = "BETA | Take a risky action in hope of getting coins and items!")
  async def lootbox(self, interaction: discord.Interaction):
    if interaction.user.id not in config.ADMIN:
      if not interaction.user.premium_since:
        return
    user_balance = db.get('economy', 'coins', interaction.user.id)
    if user_balance < 5:
      await interaction.response.send_message("You're too poor to open a lootbox. Save up at least <:coins:1172819933093179443> ` 5 Coins ` to get started.",ephemeral=True)
      return
    embed = discord.Embed(description="**How it works**\nYou can open lootboxes for how long you want, the first lootbox costs <:coins:1172819933093179443> ` 5 Coins ` and its price will graudually increase.\nYou can get more coins, items, and even rare items!\n\n**But there's a catch:** There is a small chance that you will loose all your opened lootboxes and the coins you spent on them.\n\n**Are you ready?**")
    embed.set_author(name='Lootbox chain!',icon_url='https://cdn-icons-png.flaticon.com/512/8580/8580823.png'	)
    embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/8832/8832614.png')
    await interaction.response.send_message(embed=embed,view=LootboxUI())

async def setup(bot):
  await bot.add_cog(Fun(bot))