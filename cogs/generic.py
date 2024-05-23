import discord
from discord import app_commands
import asyncio
import db
import config
import random
from core.plugins import Plugin
from typing import List
from core.casino import GameMenu
from core.misc import calculate_boosts, hascoins
from core.items import getItemByID
from core.ui import LootboxUI, LOOTBOX_PRICE
from core.emojis import *

SLOT_MACHINE_PRICE = 100
SLOTS = [":apple:", ":banana:",":watermelon:", COINS_EMOJI, LEVEL_EMOJI,SANDCLOCK_EMOJI]


class Generic(Plugin):
  def __init__(self, bot):
    self.bot = bot
    super().__init__(bot=bot)
    

  @app_commands.command(name = "coems",description = "Silly coems generator!")
  @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id,i.user.id))
  async def coems(self, interaction: discord.Interaction):
    item = db.items.get(interaction.user.id,1001)
    if item == 0:
      await interaction.response.send_message(f"You didn't buy this feature yet.\nSave up {COINS_EMOJI} ` 350 Coins ` and get it in the <#{config.SHOP_CHANNEL}>!",ephemeral=True)
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
  @hascoins(50,'start a casino session')
  async def casino(self, interaction: discord.Interaction, mode: app_commands.Choice[str] = None,bet: int = None):
    host_balance = db.users.get('coins',interaction.user.id)
    if not bet:
      bet = 0
    else:
      if host_balance < bet:
        await interaction.response.send_message("You have insufficient funds.",ephemeral=True)
        return
      if bet not in range(50,1500):
        await interaction.response.send_message(f'Your Bet must be at least {COINS_EMOJI} ` 50 - 1500 Coins `',ephemeral=True)
        return
    host = interaction.user
    msg = f'{WORLDWIDE_EMOJI} ` Public `'
    key = None
    if mode:
      if mode.value == 'true':
        msg = f'{PADLOCK_EMOJI} ` Private `'
        key = random.randint(1000,9999)
    embed = discord.Embed(title=f'{POKER_EMOJI} Casino Session',description=f"**Host:** {host.mention}\n**Lobby:** {msg}")
    await interaction.response.send_message(embed=embed,view=GameMenu(key,host.id,bet))


  @app_commands.command(name = "chatrevive",description = "Pings a role to revive the chat!")
  @app_commands.checks.cooldown(1, 1600, key=lambda i: (i.guild_id))
  async def chatrevive(self, interaction: discord.Interaction):
    item = db.items.get(interaction.user.id,1002)
    if item == 0:
      await interaction.response.send_message(f"You didn't buy this feature yet.\nSave up {COINS_EMOJI} ` 400 Coins ` and get it in the <#{config.SHOP_CHANNEL}>!",ephemeral=True)
    else:
      await interaction.response.send_message("Pinging the kittens...",ephemeral=True,delete_after=3)
      await interaction.channel.send(f"**{interaction.user.mention} Pinged <@&1139862719726624768>! :smile:**")

  async def item_autocomplete(self, interaction: discord.Interaction, current: str):
      items = [getItemByID(item.id) for item in db.items.all(interaction.user.id)]
      return [
          app_commands.Choice(name=item.name, value=str(item.id))
          for item in items if current.lower() in item.name.lower()
      ]

  @app_commands.command(name="use", description="uses an item from your inventory")
  @app_commands.autocomplete(item=item_autocomplete)
  @app_commands.describe(item='The item you want to use.')
  async def use(self, interaction: discord.Interaction, item: str):
    fullitem = getItemByID(int(item))
    # TODO Will implement await useitem(itemid) in future
    await interaction.response.send_message(f"**{interaction.user.mention}** used **{fullitem.name}**")
  
  @app_commands.command(name = "daily",description = "Claim your daily coins!")
  @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id,i.user.id))
  async def daily(self, interaction: discord.Interaction):
    raise NotImplementedError("This command is not implemented yet.")

  @app_commands.command(name = "lootbox",description = "Take a risky action in hope of getting coins and items!")
  @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id,i.user.id))
  @hascoins(LOOTBOX_PRICE,'open a lootbox')
  async def lootbox(self, interaction: discord.Interaction):
    embed = discord.Embed(description=f"**How it works**\nYou can open lootboxes for how long you want.\nEach box costs {COINS_EMOJI} ` {LOOTBOX_PRICE} Coins `\nYou can get more coins, and even rare items!\n\n**But there's a catch:** There is a small chance that you will loose all your opened lootboxes and the coins you spent on them.\n\n**Are you ready?**")
    embed.set_author(name='Lootbox chain!',icon_url='https://cdn-icons-png.flaticon.com/512/8580/8580823.png'	)
    embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/8832/8832614.png')
    await interaction.response.send_message(embed=embed,view=LootboxUI(interaction.user))

  @app_commands.command(description="Take a risky action in hope of getting boosts!")
  @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
  @hascoins(SLOT_MACHINE_PRICE,'play the slot machine')
  async def slotmachine(self, interaction: discord.Interaction):
      db.exchange(interaction.client.user.id, interaction.user.id, SLOT_MACHINE_PRICE)
      for _ in range(8):
          slots = [random.choice(SLOTS) for _ in range(3)]
          slotformat = ' : '.join(slots)
          embed = discord.Embed(description=f"{slotformat}\n\n")
          embed.set_author(name='Slot Machine', icon_url='https://cdn-icons-png.flaticon.com/128/7370/7370028.png')

          if interaction.response.is_done():
              await interaction.edit_original_response(embed=embed)
          else:
              await interaction.response.send_message(embed=embed)

      slot1, slot2, slot3 = slots

      # Final result
      if slot1 == slot2 == slot3:
          embed.description += '**Jackpot!** '
          if slot1 in [":apple:", ":banana:", ":cherries:", ":grapes:", ":watermelon:"]:
              embed.description += f"**You got the ` Golden {slot1.split(':')[1].capitalize()} `**"
          elif slot1 == COINS_EMOJI:
              embed.description += "**You got a ` 30 minute coin boost `**"
              db.items.delta(interaction.user.id, 4002, 30*60)
          elif slot1 == LEVEL_EMOJI:
              embed.description += "**You got a ` 30 minute XP boost `**"
              db.items.delta(interaction.user.id, 4001, 30*60)
          else:
              embed.description += "**You got a ` 30 minute Shop discount `**"
              db.items.delta(interaction.user.id, 4003, 30*60)
      else:
          matched, unique_matches, boosts, boost_durations = calculate_boosts(slots)

          if len(unique_matches) > 1:
              embed.description += '**Lucky! You got:**'
          elif len(unique_matches) == 1:
              embed.description += '**Nice! You got:**'
          else:
              embed.description += '**Better luck next time!**'

          for slot in unique_matches:
              count = matched.count(slot)
              if count in boost_durations:
                  db.items.delta(interaction.user.id, boosts[slot][1], boost_durations[count])
                  embed.description += f'\n***{boosts[slot][0]}*** ` {boost_durations[count] // 60} minutes `'

      await interaction.edit_original_response(embed=embed)

async def setup(bot):
  await bot.add_cog(Generic(bot))
