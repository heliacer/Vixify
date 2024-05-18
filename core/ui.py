import discord
from discord import ui
import asyncio
import db
import random
from typing import List  
from core.helpers import winchance

LOOTBOX_PRICE = 5

class LootboxUI(ui.View):
  def __init__(self,next=True,index=1,total_rewards=[]):
    super().__init__()
    self.index: int = index
    self.total_rewards: list = total_rewards
    if next:
      openButton = ui.Button(label='Open lootbox', emoji='<:checkout:1175007951669436446>', style=discord.ButtonStyle.primary)
      openButton.callback = self.open
      self.add_item(openButton)
    if self.index > 1:
      claimButton = ui.Button(label='Claim All', emoji='<:features:1178989659976642581>', style=discord.ButtonStyle.gray)
      claimButton.callback = self.claim
      self.add_item(claimButton)

  async def open(self, interaction: discord.Interaction):
    user_balance = db.get('economy', 'coins', interaction.user.id)
    embed1 = discord.Embed(description='<a:loading:1239608763447640114> ***Opening lootbox...***', color=discord.Color.blurple())
    await interaction.response.edit_message(embed=embed1, view=None)
    await asyncio.sleep(1)
    embed2 = discord.Embed()
    db.exchange(interaction.client.user.id,interaction.user.id,LOOTBOX_PRICE)
    if winchance(80):
      rewards = ['undefined', 'still need to implement this part', 'but you get the idea']
      
      self.total_rewards.extend(rewards)
      embed2.description = "**You opened a lootbox and found:**\n- {}".format('\n- '.join(rewards))
      embed2.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/7839/7839136.png')
      if user_balance < LOOTBOX_PRICE :
          embed2.description += f'\nAnd you spent all your money! No more lootboxes for you!'
          self.setday(interaction.user.id)
      await interaction.edit_original_response(embed=embed2,view=LootboxUI(
        next=user_balance > LOOTBOX_PRICE,
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

class GameCheckoutGUI(discord.ui.View):
  def __init__(self,players: list,winners: List[List[int]],seconds):
    super().__init__(timeout=None)
    self.players = players
    self.winners = winners
    payout_button = discord.ui.Button(label=f'Proceed to payout ({seconds})',style=discord.ButtonStyle.blurple,emoji='<:checkout:1175007951669436446>')
    payout_button.callback = self.payout
    self.add_item(payout_button)

  async def payout(self,interaction: discord.Interaction = None,message: discord.Message = None):
    quote = random.choice["There are no losers, just quitters","99% of gamblers quite before they win","keep your eyes on the prize","The house always wins"]
    if self.winners:
      pot = sum(item[1] for item in self.players)
      embed = discord.Embed(description='')
      for winner in self.winners:
        db.exchange(winner[0],interaction.client.user.id,pot/len(self.winners))
        embed.description += f"<@{winner[0]}> got paid <:coins:1172819933093179443>` {pot} Coins `\n*{quote}*"
    else:
      embed = discord.Embed(description=f'**All gamblers recieve their money back due to a draw.**{quote}')
    embed.set_author(name='Gambling Checkout',icon_url='https://cdn-icons-png.flaticon.com/128/8580/8580823.png')
    if interaction:
      await interaction.message.delete()
      await interaction.channel.send(embed=embed)
    if message:
      print(message)
      await message.delete()
      await message.channel.send(embed=embed)