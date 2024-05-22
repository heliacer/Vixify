import discord
import db
import random
from discord import app_commands
from discord.ext import commands
from core.misc import loadbarimage, winchance, isprivileged
from core.items import getItemBoard
from core.plugins import Plugin

class Economy(Plugin):
  def __init__(self, bot):
    self.bot = bot
    super().__init__(bot=bot)

  @commands.hybrid_command(name= "bank", description = 'The Vixify Bank gross value')
  async def bank(self,ctx):
    bank_balance = db.users.get("coins",self.bot.user.id)
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
    coins_balance = db.users.get("coins",user.id)
    user_rank = db.users.get("rank",user.id)
    user_xp = db.users.get("xp",user.id)
    if user_xp > 0:
      if user_rank > 0:
        percentage = (int(user_xp) / ((int(user_rank))*120)) * 100
      else:
        percentage = int(user_xp) / 40 * 100
    else: percentage= 0
    file = discord.File(fp=loadbarimage(percentage),filename="xp.png")
    embed = discord.Embed(description=f"**<:coins:1172819933093179443> ` {coins_balance:,} Coins ` <:level:1172820830812643389> `` Rank {user_rank} ``**")
    embed.set_author(name = f"{user.display_name}'s balance",icon_url = user.avatar.url)
    embed.set_thumbnail(url="attachment://xp.png")
    await ctx.send(embed = embed,file=file)
    
  @commands.hybrid_command(name = "steal",description = "steality steality")
  @commands.cooldown(1, 180, commands.BucketType.user)
  @app_commands.describe(member = "Member to steal from")
  async def steal(self, ctx: commands.Context, member : discord.Member):
    user = ctx.author
    if user == member:
      await ctx.send("You cannot steal from yourself.",ephemeral=True,delete_after = 10)
      return
    if member.bot:
      await ctx.send(f"{member.mention} is a bot.\nBots don't have coins. lmao.")
      return
    
    user_rank = db.users.get("rank",user.id)
    member_rank = db.users.get("rank",member.id)
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
    
    user_balance = db.users.get("coins",user.id)

    if user_balance == 0:
        await ctx.send("You don't have any Coins left.", ephemeral=True, delete_after=10)
        return
    
    member_balance = db.users.get("coins",member.id)
    member_padlock = db.items.get(member.id,2001)

    if member_padlock != 0:
      embed = discord.Embed(description=f"**<:padlock:1178730730998734980> {member.name} had a padlock.**")
      dm = discord.Embed(description=f"**{user.mention} tried to steal from you.**",color = 0x2b2d31)
      if winchance(20):
        db.items.inc(member.id,2001,-1)
        embed.description += f"\n**You managed to break the padlock**"
        dm.description += f"\n**Unfortunately, {user.mention} managed to break your padlock, without any lockpick.**"
        if winchance(50):
          padlock_stolen = min(1,round(member_balance*0.05))
          db.exchange(user.id,member.id,padlock_stolen)
          embed.description += f"\n**and stole a small amount of ` {padlock_stolen} Coins `.**"
          dm.description += f"\n**A small amount of your coins were stolen.**"
        else:
          embed.description += f"\n**,and got away with zero coins.**"
          dm.description += f"\n**None of your coins were stolen.**"
      else:
        db.exchange(self.bot.user.id,user.id,round(user_balance*0.3))
        embed.description += f"\n**You lost a lot of coins. Better luck next time.**"
        dm.description += f"\n**Luckily, {user.mention} failed to break the padlock.**"
      await ctx.send(embed=embed)
      await member.send(embed=dm) if member.dm_channel else None
      return

    elif member_balance == 0:
        await ctx.send(f"{member.mention} doesn't have any Coins.", ephemeral=True, delete_after=10)
        return
    
    success = winchance(65)

    if success:
      steal_amount = round(member_balance*0.1)
      if member_balance > user_balance:
         steal_amount= round(user_balance*0.15)
      if user_balance < 20:
        steal_amount = user_balance
      member_new_balance = member_balance - steal_amount

      db.exchange(user.id,member.id,steal_amount)
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
         
      db.exchange(self.bot.user.id,user.id,pay_amount)

      embed = discord.Embed(description = f"` {user} ` tried robbing from you\nAnd paid <:coins:1172819933093179443> ` {pay_amount:,} Coins ` in return",color = 0x2b2d31)
      await member.send(embed = embed) if member.dm_channel else None

      embed = discord.Embed(description = f"**{failMessage}**",color = 0xfa7a7a)
      await ctx.send(embed = embed)

  @commands.hybrid_command(name = "share",description = "Share coins to other users")
  @app_commands.describe(amount = "amount of coins to share")
  async def share(self, ctx: commands.Context, member : discord.Member, amount : int):
    if member == ctx.author:
      await ctx.send("You can't share yourself coins.",ephemeral=True,delete_after = 10)
      return
    if amount < 0:
      await ctx.send("You cannot send negative funds.",ephemeral=True,delete_after = 10)
      return
    if member.bot and member.id != self.bot.user.id:
      await ctx.send(f"{member.mention} is a bot.\nAre you a bot aswell?")
      return
    user = ctx.author
    user_balance = db.users.get("coins",user.id)
    member_balance = db.users.get("coins",member.id)

    if not user_balance or user_balance == 0:
      await ctx.send("You don't have any coins.",ephemeral = True,delete_after = 10)
      return
    if not member_balance or member_balance == 0:
      await ctx.send(f"{member.mention} doesn't have any coins.",ephemeral = True,delete_after = 10)
      return
    if amount > user_balance:
      await ctx.send(f"You can only send up to <:coins:1172819933093179443> ` {user_balance:,} Coins `",ephemeral = True,delete_after = 10)
      return
    db.exchange(member.id,user.id,amount)
    embed = discord.Embed(description = f"**Successfully shared <:coins:1172819933093179443> ` {amount:,} Coins ` with {member.mention}!**",color = 0x7afa89)
    await ctx.send(embed = embed)

  @app_commands.command(name="leaderboard",description="See who is on the top")
  @app_commands.describe(max="Maximum members to display")
  async def leaderboard(self,interaction:discord.Interaction,max: int = 15):
    items = db.board("coins",max)
    print(items)
    # TODO fix some bugs ( they will come up )
    bank = items[0][1]
    del items[0]
    embed= discord.Embed(title="<:coins:1172819933093179443> Coins Leaderboard",description=f'**Bank** `` {bank:,} Coins ``\n\n' + '\n'.join(f"**<@{row[0]}> `` {row[1]} Coins ``**" for row in items))
    await interaction.response.send_message(embed=embed)

  @app_commands.command(name="inventory", description="View owned items & features")
  async def inventory(self, interaction: discord.Interaction, member: discord.Member = None):
    user = member or interaction.user
    if user != interaction.user and not isprivileged(interaction.user):
      await interaction.response.send_message(
        "**<:level:1172820830812643389> Viewing other's inventory requires you to be a booster of this server.**",
          ephemeral=True
        )
      return

    items = db.items.all(user.id)
    embed = discord.Embed(description="")
    embed.set_author(name=f"{user.display_name}'s Inventory", icon_url=user.avatar.url)
    embed.description = getItemBoard(items)
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
  await bot.add_cog(Economy(bot))