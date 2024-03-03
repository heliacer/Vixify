import discord
import json
import config
from dbmanager import *
from discord.ext import commands
import traceback

ranks = json.load(open("assets/ranks.json")).items()

class Events(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message : discord.Message):
    if not message.author.bot:
      coins_new = len(message.content) // 8 if any(role.id == config.booster_role for role in message.author.roles) else len(message.content) // 10
      xp_new = len(message.content) // 4
      user_id = message.author.id
      user_rank = get("economy","rank",user_id)
      user_xp = get("economy","xp",user_id)
      bank_balance = get('economy','coins',self.bot.user.id)
      rank_new= 0
      if user_rank != 0:
        if user_xp + xp_new >= (user_rank)*120:
          while user_xp + xp_new >= (user_rank)*120:
            rank_new+=1
            msg = ""
            for key, value in ranks:
              if value["rank"] == user_rank+rank_new:
                  role = message.guild.get_role(value["roleid"])
                  if role:
                    await message.author.add_roles(role)
                    msg = f"\n You just gathered `` {role.name} ``"
            xp_new = xp_new- ((user_rank)*120-120)
            user_xp = 0
          await message.channel.send(f"**Congrats {message.author.mention}, You just reached <:level:1172820830812643389> `` Rank {user_rank+rank_new} ``{msg}**",allowed_mentions=None)
      else:
        if user_xp+xp_new> 15:
          rank_new+=1
          await message.channel.send(f"**:tada: Congrats {message.author.mention}, You just reached <:level:1172820830812643389> `` Rank {user_rank+rank_new} `` !\n\nTIP:** *You can exchange coins earned by chatting in <#{1142779979931856896}>.\nEnjoy your stay!*")
          user_xp = 0
          xp_new = xp_new-15
      set("economy","rank",user_id,user_rank+rank_new)
      set("economy","xp",user_id,xp_new+user_xp)
      if bank_balance < coins_new:
        if not bank_balance == 0:
          exchange(user_id,self.bot.user.id,bank_balance)
          await message.channel.send('@everyone :megaphone: The Bank is empty!!! No more coin rewards!!! All items are on 50% Sale go go go buy now !!!')
        else:
          pass
      else:
        if bank_balance - coins_new < message.guild.member_count*100 and not bank_balance < message.guild.member_count*100:
          await message.channel.send('@everyone :megaphone: The bank is getting emptier... All items are on 75% Sale!!!')
        exchange(user_id,self.bot.user.id,coins_new)
  @commands.Cog.listener()
  async def on_member_join(self,member):
    current = get("economy","coins",self.bot.user.id)
    set("economy","coins",self.bot.user.id,current+500)

async def setup(bot):
  await bot.add_cog(Events(bot))