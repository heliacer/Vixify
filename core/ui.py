import discord
from discord import ui
from datetime import datetime
import asyncio
import db
import random
from typing import List  
from core.misc import winchance
from collections import Counter
from core.items import getRandomItemByRarity,getItems,getItemByID,getItemBoard,Item

LOOTBOX_PRICE = 50

class LootboxUI(ui.View):
  def __init__(self,user: discord.Member,next: bool=True,index: int=1,total_rewards: List[Item]=[]):
    super().__init__()
    self.user = user
    self.index = index
    self.total_rewards = total_rewards
    
    # list of items which only can be owned once that the user owns
    owned = set(item.id for item in db.items.getall(user.id) if getItemByID(item.id).ownstack == 1)
    self.query = [item for item in getItems() if item.id not in owned and item.type not in ['role','command']]

    if next:
      openButton = ui.Button(label='Open lootbox', emoji='<:checkout:1175007951669436446>', style=discord.ButtonStyle.primary)
      openButton.callback = self.open
      self.add_item(openButton)
    if self.index > 1:
      claimButton = ui.Button(label='Claim All', emoji='<:features:1178989659976642581>', style=discord.ButtonStyle.gray)
      claimButton.callback = self.claim
      self.add_item(claimButton)

  async def open(self, interaction: discord.Interaction):
    if interaction.user != self.user:
      await interaction.response.send_message('You are not allowed to open lootboxes for other users!', ephemeral=True)
      return
    user_balance = db.fetch('economy', 'coins', interaction.user.id)
    embed1 = discord.Embed(description='<a:loading:1239608763447640114> ***Opening lootbox...***', color=discord.Color.blurple())
    await interaction.response.edit_message(embed=embed1, view=None)
    await asyncio.sleep(1)
    embed2 = discord.Embed()
    db.exchange(interaction.client.user.id,interaction.user.id,LOOTBOX_PRICE)
    if winchance(80):
      reward = getRandomItemByRarity(1,self.query)
      self.total_rewards.append(reward)
      embed2.description = f"**You opened a lootbox and found {reward.name}!**\n\n*Type:* ` {reward.type} ` *Rarity:* ` {reward.rarity} ` *Value:* <:coins:1172819933093179443> ` {reward.price} Coins `"
      embed2.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/7839/7839136.png')
      if user_balance < LOOTBOX_PRICE :
          embed2.description += f'\nAnd you spent all your money! No more lootboxes for you!'
      await interaction.edit_original_response(embed=embed2,view=LootboxUI(
        user=self.user,
        next=user_balance > LOOTBOX_PRICE,
        index=self.index + 1,
        total_rewards=self.total_rewards
        ))
    else:
      embed2.description = f'**You opened a Lootbox and found nothing!**\n\nYou lost all your opened lootboxes and <:coins:1172819933093179443> ` {self.index * LOOTBOX_PRICE} Coins `!'
      embed2.set_thumbnail(url='https://cdn-icons-png.flaticon.com/128/3741/3741593.png')
      self.reset()
      await interaction.edit_original_response(embed=embed2, view=None)

  async def claim(self, interaction: discord.Interaction):
    # TODO : add roles correctly
    for reward in self.total_rewards:
      if reward.type == 'role':
        if interaction.guild.get_role(reward.id) and reward.id not in [role.id for role in interaction.user.roles]:
          await interaction.user.add_roles(reward.id)
      else:
        db.items.increase(interaction.user.id,reward.id)

    itemsmerged = Counter(item.id for item in self.total_rewards)
    baseitems = [db.BaseItem(item_id, [total_amount]) for item_id, total_amount in itemsmerged.items()]
    itemboard = getItemBoard(baseitems)

    embed = discord.Embed(description=f'**<:partyhorn:1175408062782263397> You claimed all rewards!**\n\n{itemboard}')
    self.reset()
    await interaction.response.edit_message(embed=embed, view=None)

  def reset(self):
    self.index = 1
    self.total_rewards = []

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