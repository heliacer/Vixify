import discord
from discord import app_commands
from casinocore import GameMenu
import asyncio
import db
import config
import random
from core.plugins import Plugin
from typing import List
from core.items import getItemByID
from core.ui import LootboxUI, LOOTBOX_PRICE

SLOT_MACHINE_PRICE = 100
SLOTS = [":apple:", ":banana:",":watermelon:", "<:coins:1172819933093179443>", "<:level:1172820830812643389>", "<:sandclock:1203261564291911680>"]


class Generic(Plugin):
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
    host_balance = db.users.get('coins',interaction.user.id)
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

  async def item_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
      items = [getItemByID(item.id) for item in db.items.all(interaction.user.id)]
      return [
          app_commands.Choice(name=item.name, value=item.id)
          for item in items if current.lower() in item.name.lower()
      ]

  @app_commands.command(name="use", description="uses an item from your inventory")
  @app_commands.autocomplete(item=item_autocomplete)
  async def use(self, interaction: discord.Interaction, item: str):
      await interaction.response.send_message(f"**{interaction.user.mention}** used **{item}**")
  
  @app_commands.command(name = "daily",description = "Claim your daily coins!")
  @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id,i.user.id))
  async def daily(self, interaction: discord.Interaction):
    raise NotImplementedError("This command is not implemented yet.")

  @app_commands.command(name = "lootbox",description = "Take a risky action in hope of getting coins and items!")
  @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id,i.user.id))
  async def lootbox(self, interaction: discord.Interaction):
    user_balance = db.users.get( 'coins', interaction.user.id)
    if user_balance < LOOTBOX_PRICE:
      await interaction.response.send_message(f"You're too poor to open a lootbox. Save up at least <:coins:1172819933093179443> ` {LOOTBOX_PRICE} Coins ` to get started.",ephemeral=True)
      return
    embed = discord.Embed(description=f"**How it works**\nYou can open lootboxes for how long you want.\nEach box costs <:coins:1172819933093179443> ` {LOOTBOX_PRICE} Coins `\nYou can get more coins, and even rare items!\n\n**But there's a catch:** There is a small chance that you will loose all your opened lootboxes and the coins you spent on them.\n\n**Are you ready?**")
    embed.set_author(name='Lootbox chain!',icon_url='https://cdn-icons-png.flaticon.com/512/8580/8580823.png'	)
    embed.set_thumbnail(url='https://cdn-icons-png.flaticon.com/512/8832/8832614.png')
    await interaction.response.send_message(embed=embed,view=LootboxUI(interaction.user))

  @app_commands.command(description="Take a risky action in hope of getting boosts!")
  @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id,i.user.id))
  async def slotmachine(self, interaction: discord.Interaction):
    user_balance = db.users.get( 'coins', interaction.user.id)
    if user_balance < SLOT_MACHINE_PRICE:
      await interaction.response.send_message(
        f"You're too poor to play the slot machine. Save up at least <:coins:1172819933093179443> ` {SLOT_MACHINE_PRICE} Coins ` to get started.",
        ephemeral=True
      )
      return
    db.exchange(interaction.client.user.id, interaction.user.id, SLOT_MACHINE_PRICE)
    for i in range(8):
      slot1, slot2, slot3 = [random.choice(SLOTS) for _ in range(3)]
      slotformat = ' : '.join([slot1, slot2, slot3])
      embed = discord.Embed(description=f"{slotformat}\n\n")
      embed.set_author(name='Slot Machine', icon_url='https://cdn-icons-png.flaticon.com/128/7370/7370028.png')

      if interaction.response.is_done():
        await interaction.edit_original_response(embed=embed)
      else:
        await interaction.response.send_message(embed=embed)

    # Final result
    if slot1 == slot2 == slot3:
      embed.description += '**Jackpot!** '
      if slot1 in [":apple:", ":banana:", ":cherries:", ":grapes:", ":watermelon:"]:
        embed.description += f"**You got the ` Golden {slot1.split(':')[1].capitalize()} `**"
      elif slot1 == "<:coins:1172819933093179443>":
        embed.description += "**You got a ` 30 minute coin boost `**"
        # TODO: Add the boost to the user
      elif slot1 == "<:level:1172820830812643389>":
        embed.description += "**You got a ` 30 minute XP boost `**"
        # TODO: Add the boost to the user
      else:
        embed.description += "**You got a ` 30 minute Shop discount `**"
        # TODO: Add the boost to the user
    else:
      boosts = {
        "<:coins:1172819933093179443>": "coin boost",
        "<:level:1172820830812643389>": "XP boost",
        "<:sandclock:1203261564291911680>": "Shop discount"
      }
      boost_durations = {
        1: "5 minutes",
        2: "10 minutes"
      }
      
      matched = [slot for slot in [slot1, slot2, slot3] if slot in boosts]
      unique_matches = set(matched)

      # TODO: check for boost, add to user
      
      if len(unique_matches) > 1:
        embed.description += '**Lucky! You got:**'
      elif len(unique_matches) == 1:
        embed.description += '**Nice! You got:**'
      else:
        embed.description += '**Better luck next time!**'
      for slot in unique_matches:
        count = matched.count(slot)
        if count in boost_durations:
          embed.description += f'\n***{boosts[slot]}*** ` {boost_durations[count]} `'
    await interaction.edit_original_response(embed=embed)

async def setup(bot):
  await bot.add_cog(Generic(bot))
