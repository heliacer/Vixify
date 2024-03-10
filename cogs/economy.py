import discord
from dbmanager import *
import random
import io
import config
import json
from discord import app_commands
from discord.ext import commands
from PIL import ImageDraw, Image, ImageFont

content = json.load(open("assets/shopindex.json"))

def getval(id,selector,section: str):
  for key,value in content[section].items():
    if value["id"] == id:
      return value[selector]


def loadbarimage(percentage: int):
    width, height = 400, 400
    image = Image.new("RGBA", (width, height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(image) 
    size = [(width / 2) - 190, (height / 2) - 190, (width / 2) + 190, (height / 2) + 190]
    draw.arc(size, -90, (percentage / 100) * 360 - 90, fill="#AF01E7", width=35)
    font = ImageFont.truetype('assets/Beyonders.ttf', 70)
    draw.text([115,70], "XP", font=font, fill="white")
    draw.text([80,180], f"{round(percentage)}%", font=font, fill="white")
    io_bytes = io.BytesIO()
    image.save(io_bytes, format="PNG")
    io_bytes.seek(0)
    return io_bytes

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.hybrid_command(name= "bank", description = 'The Vixify Bank gross value')
  async def bank(self,ctx):
    bank_balance = get("economy","coins",self.bot.user.id)
    status = ['Healthy','Sufficient funds, stable operations.']
    if bank_balance < ctx.guild.member_count *100:
      status = ['Undercapitalized','Running low on funds, 75% Shop goods sale.']
      if bank_balance == 0:
        status = ['Insolvent','Critical funds, 50% Shop goods sale.']
    embed = discord.Embed(title='Bank',description=f"**<:vix:1196888520602689607> ` {bank_balance} Coins `** **Status:** ` {status[0]} ` \n*{status[1]}*")
    await ctx.send(embed=embed)

  @commands.hybrid_command(name = "coins",description = "Coins & Level stats")
  @app_commands.describe(member = "A server member")
  async def coins(self, ctx, member : discord.Member = None):
    user = member or ctx.author
    if user.bot:
      if user.id == self.bot.user.id:
        await ctx.send(f"Use ` ?bank ` to view {self.bot.user.mention}'s coins")
      else:
        await ctx.send(f"{user.mention} is a Bot.\nBots don't have coins. lol.")
      return
    coins_balance = get("economy","coins",user.id)
    user_rank = get("economy","rank",user.id)
    user_xp = get("economy","xp",user.id)
    if user_xp > 0:
      if user_rank > 0:
        percentage = (int(user_xp) / ((int(user_rank))*120)) * 100
      else:
        percentage = int(user_xp) / 40 * 100
    else: percentage= 0
    file = discord.File(fp=loadbarimage(percentage),filename="xp.png")
    embed = discord.Embed()
    embed.set_author(name = f"{user.display_name}'s balance",icon_url = user.avatar.url)
    embed.set_thumbnail(url="attachment://xp.png")
    if coins_balance > 0:
      embed.description = f"**<:coins:1172819933093179443> ` {coins_balance:,} Coins ` <:level:1172820830812643389> `` Rank {user_rank} ``**"
    else:
      embed.description = f"**<:coins:1172819933093179443> ` 0 Coins ` <:level:1172820830812643389> ` Rank {user_rank} ` <- Broke,** *sniff*"
    await ctx.send(embed = embed,file=file)
    
  @commands.hybrid_command(name = "steal",description = "steality steality")
  @commands.cooldown(1, 180, commands.BucketType.user)
  @app_commands.describe(member = "Member to steal from")
  async def steal(self, ctx, member : discord.Member):
    user = ctx.author
    if user == member:
      await ctx.send("You cannot steal from yourself.",ephemeral=True,delete_after = 10)
      return
    if member.bot:
      await ctx.send(f"{member.mention} is a bot.\nBots don't have coins. lmao.")
      return
    
    user_rank = get("economy","rank",user.id)
    member_rank = get("economy","rank",member.id)
    if user_rank < 3:
      embed = discord.Embed(description="You need to reach <:level:1172820830812643389> `` Rank 2 `` to be able to steal.")
      embed.set_author(name='Nuh uh',url='https://discord.com/assets/b2dac9e1b4de07c5ae68.svg')
      await ctx.send(embed=embed)
      return
    if member_rank < 3:
      embed = discord.Embed(description="You may not steal from users lower than `` Rank 2 ``. They're newbies, mafaka.")
      embed.set_author(name='Nuh uh',url='https://discord.com/assets/b2dac9e1b4de07c5ae68.svg')
      await ctx.send(embed=embed)
      return
    
    user_balance = get("economy","coins",user.id)
    member_balance = get("economy","coins",member.id)
    json_data = get("items","json_data",member.id)

    if json_data != 0:
      json_data = json.loads(json_data)
      if json_data['1001']:
        if json_data['1001'] > 0:
          json_data['1001'] -= 1
          set("items","json_data", member.id,json.dumps(json_data))
          if user_balance < 20:
            set("economy","coins",user.id,0)
            embed = discord.Embed(description=f"**<:padlock:1178730730998734980> {member.name} had a padlock. you lost ALL your coins**")
          else:
            set("economy","coins",user.id,round(user_balance-user_balance*0.5))
            embed2 = discord.Embed(description=f"While you had a padlock, {user.display_name} tried stealing from you and litteraly lost half of his Coins. You monster.",color = 0x2b2d31)
            embed = discord.Embed(description=f"**<:padlock:1178730730998734980> {member.name} had a padlock. dammn bro you lost half of your coins**")
          await ctx.send(embed=embed)
          await member.send(embed=embed2) if member.dm_channel else None
          return

    if user_balance == 0:
        await ctx.send("You don't have any Coins left.", ephemeral=True, delete_after=10)
        return
    elif member_balance == 0:
        await ctx.send(f"{member.mention} doesn't have any Coins.", ephemeral=True, delete_after=10)
        return
    
    success = random.choice([True,True, False])

    if success:
      steal_amount = round(member_balance*0.1)
      if member_balance > user_balance:
         steal_amount= round(user_balance*0.15)
      if user_balance < 20:
        steal_amount = user_balance
      user_new_balance = user_balance + steal_amount
      member_new_balance = member_balance - steal_amount

      set("economy","coins",user.id,user_new_balance)
      set("economy","coins",member.id,member_new_balance)

      embed = discord.Embed(
        description = f"**` {user} ` stole <:coins:1172819933093179443> ` {steal_amount:,} Coins ` from you.\nYou now have <:coins:1172819933093179443> ` {member_new_balance:,} coins ` left**",
        color = 0x2b2d31
      )
      await member.send(embed=embed) if member.dm_channel else None

      embed = discord.Embed(description = f"**You managed to steal a small amount of <:coins:1172819933093179443> ` {steal_amount:,} Coins ` from {member.mention}**", color= 0x7afa89)
      await ctx.send(embed = embed)
    else: # If not Success
      pay_amount = round(user_balance*0.3)
      failMessagesList = [
        f"You tried to steal from {member.mention} and paid <:coins:1172819933093179443> ` {pay_amount:,} Coins ` Lol",
        f"You failed stealing {member.mention} and paid <:coins:1172819933093179443> ` {pay_amount:,} Coins `",
        f"You got caught and paid {member.mention} <:coins:1172819933093179443> ` {pay_amount:,} Coins ` lmao"
      ]
      failMessage = random.choice(failMessagesList)
      if user_balance < 20:
         pay_amount = user_balance
         failMessage = f"You failed and lost all your Coins to {member.mention}"
         
      exchange(config.bot_id,user.id,pay_amount)

      embed = discord.Embed(description = f"` {user} ` tried robbing from you\nAnd paid <:coins:1172819933093179443> ` {pay_amount:,} Coins ` in return",color = 0x2b2d31)
      await member.send(embed = embed) if member.dm_channel else None

      embed = discord.Embed(description = f"**{failMessage}**",color = 0xfa7a7a)
      await ctx.send(embed = embed)

  @commands.hybrid_command(name = "share",description = "Share coins to other users")
  @app_commands.describe(amount = "amount of coins to share")
  async def share(self, ctx, member : discord.Member, amount : int):
    if member == ctx.author:
      await ctx.send("You can't share yourself coins.",ephemeral=True,delete_after = 10)
      return
    if amount < 0:
      await ctx.send("You cannot send negative funds.",ephemeral=True,delete_after = 10)
      return
    if member.bot and member.id != config.bot_id:
      await ctx.send(f"{member.mention} is a bot.\nAre you a bot aswell?")
      return
    user = ctx.author
    user_balance = get("economy","coins",user.id)
    member_balance = get("economy","coins",member.id)

    if not user_balance or user_balance == 0:
      await ctx.send("You don't have any coins.",ephemeral = True,delete_after = 10)
      return
    if not member_balance or member_balance == 0:
      await ctx.send(f"{member.mention} doesn't have any coins.",ephemeral = True,delete_after = 10)
      return
    if amount > user_balance:
      await ctx.send(f"You can only send up to <:coins:1172819933093179443> ` {user_balance:,} Coins `",ephemeral = True,delete_after = 10)
      return
    user_new_balance = user_balance - amount
    member_new_balance = member_balance + amount
    set("economy","coins",user.id,user_new_balance)
    set("economy","coins",member.id,member_new_balance)
    embed = discord.Embed(description = f"**Successfully shared <:coins:1172819933093179443> ` {amount:,} Coins ` with {member.mention}!**",color = 0x7afa89)
    await ctx.send(embed = embed)

  @app_commands.command(name="leaderboard",description="See who is on the top")
  @app_commands.describe(max="Maximum members to display")
  async def leaderboard(self,interaction:discord.Interaction,max: int = 15):
    items = board("coins",max)
    bank = items[0][1]
    del items[0]
    embed= discord.Embed(title="<:coins:1172819933093179443> Coins Leaderboard",description=f'**Bank** `` {bank} Coins ``\n\n' + '\n'.join(f"**<@{row[0]}> `` {row[1]} Coins ``**" for row in items))
    await interaction.response.send_message(embed=embed)

  @app_commands.command(name="inventory",description="View owned items & features")
  async def inventory(self,interaction:discord.Interaction,member:discord.Member=None):
    user = member or interaction.user
    role = interaction.guild.get_role(config.booster_role)
    if role:
      if role in interaction.user.roles or user == interaction.user:
        json_data = get("items","json_data",user.id)
        if json_data != 0:
          json_data = json.loads(json_data)
          listing = []
          for key, value in json_data.items():
            if json_data[key] != 0:
              listing.append(f'**{json_data[key]}x {getval(int(key),"name","items")}**')
              value = '\n'.join(item for item in listing)
          if not listing:
            value = "No items left, lol."
        else:
          value = "No Items here, lol."
        embed = discord.Embed(description=value)
        embed.set_author(name=f"{user.name}'s Inventory",icon_url=user.avatar.url)
        await interaction.response.send_message(embed=embed,ephemeral=True)
      else:
        await interaction.response.send_message("You need to be a Server Booster to be able to view other's inventory.",ephemeral=True)
    else:
      await interaction.response.send_message("No Booster Role found.")
    
async def setup(bot):
  await bot.add_cog(Economy(bot))