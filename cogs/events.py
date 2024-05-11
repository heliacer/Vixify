import discord
import json
import config
import db
from discord.ext import commands
import traceback
import math
import datetime

# TODO: this needs some serious refactoring and cleanup - it's a mess

# TODO: make a type listener which will bypass heat addition after typing for a certain amount of time ( 20 seconds )

THRESHOLD = 30
ranks = json.load(open("assets/ranks.json")).items()
messages = {}
warnings = {}
has_penalty = {}
typing_duration = {}

#  calcualtes the heat of messages (2) and their time difference
def calc_message(user_messages):
    heat = 0
    time_diff = None
    if user_messages:
        length, timestamp = user_messages[-1]
        heat += length
        if len(user_messages) > 1:
            prev_length, prev_timestamp = user_messages[-2]
            heat += prev_length
            time_diff = (timestamp - prev_timestamp).total_seconds()
            heat = heat * max(int(THRESHOLD - time_diff),1)
    return heat,time_diff # returns heat and time difference between the messages

# calculates the cooldown for a message
def calc_cooldown(message):
    timediff = datetime.timedelta(seconds=0)
    current_time = datetime.datetime.now(datetime.UTC) 
    while calc_message([message, (1, current_time + timediff)])[0] > 20000:
        timediff += datetime.timedelta(seconds=1)
        print(timediff.total_seconds())
    return int(timediff.total_seconds())

async def broadcast(message: discord.Message,content,title=None,view=None,thumb_url=None):
  embed = discord.Embed(description=content,title=title)
  embed.set_thumbnail(url=thumb_url)
  try:
    dm = await message.author.create_dm()
    await dm.send(embed=embed,view=view)
  except Exception as e:
    print(e)
    await message.channel.send(embed=embed,view=view)

class ConfirmDeclineButtons(discord.ui.View):
  def __init__(self,original_message: discord.Message):
    super().__init__(timeout=None)
    self.original_message = original_message

  @discord.ui.button(label="Accept",emoji='<:confirm:1175396326272409670>')
  async def accept(self,interaction: discord.Interaction,button: discord.ui.Button):
    await interaction.response.edit_message(view=None)
    await broadcast(message=self.original_message,content=f"<:partyhorn:1175408062782263397> Your Appeal was accepted by {interaction.user.mention}. Happy you're back!\nPlease excuse any mistakes we have made. We try to constantly improve.",thumb_url='https://media1.tenor.com/m/KhtKI4EkuR0AAAAd/seal-silly.gif')
    await self.original_message.author.timeout(None)
    await self.original_message.channel.send(f"Recovered message by {self.original_message.author.mention}:\n\n{self.original_message.content}")
    await interaction.channel.send(f'<:passion:1179088197842649180> Thanks for your feedback and hard work, {interaction.user.mention}')

  @discord.ui.button(label="Decline",emoji='<:remove:1175005705422512218>')
  async def decline(self,interaction: discord.Interaction,button: discord.ui.Button):
    await interaction.response.edit_message(view=None)
    await broadcast(message=self.original_message,content=f"<:remove:1175005705422512218> Your Appeal was declined by {interaction.user.mention}. We're sorry.",thumb_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSVdxamPXtGCZdAwZSGvZIz95afqYpIEYYLiQNA-v5WZwkXTirx')
    await interaction.channel.send(f'<:passion:1179088197842649180> Thanks for your feedback and hard work, {interaction.user.mention}')

class AppealButton(discord.ui.View):
  def __init__(self,channel: discord.TextChannel,original_message: discord.Message):
    super().__init__(timeout=None)
    self.channel = channel
    self.original_message = original_message

  @discord.ui.button(label="Appeal",emoji='<:send:1215938286204489809>')
  async def appeal(self,interaction: discord.Interaction,button: discord.ui.Button):
    update_embed = discord.Embed(title='Long Message spam appeal',description=f'{self.original_message.author.mention} sent a message in {self.original_message.channel.mention} and would like to appeal:\n\n>>> {self.original_message.content}')
    await self.channel.send(embed=update_embed,view=ConfirmDeclineButtons(self.original_message))
    button.disabled = True
    await interaction.response.edit_message(view=self)
    await interaction.channel.send('<:confirm:1175396326272409670> Appeal sent. Please wait until it has been revieved.')

def is_author(message: discord.Message, member: discord.Member):
    return message.author == member

def has_admin():
    def predicate(ctx: commands.Context):
        return ctx.message.author.guild_permissions.administrator
    return commands.check(predicate)

class Events(commands.Cog):
  def __init__(self, bot : discord.Client):
    self.bot = bot
  
  @commands.command(name='clearheat')
  @has_admin()
  async def clearheat(self,ctx: commands.Context,member: discord.Member):
    messages[member.id] = []
    warnings[member.id] = []
    has_penalty[member.id] = False
    await ctx.send(f'<:confirm:1175396326272409670> Heat cleared for {member.mention}')

  @commands.Cog.listener()
  async def on_message(self, message : discord.Message):
    if message.author.bot: return
    if not message.guild: return

    # ignore the coders B)
    while "```" in message.content:
      start = message.content.find("```")
      end = message.content.find("```",start+3)
      message.content = message.content[:start] + message.content[end+3:]

    # add heat, calculate stuff
    content_length = len(message.content)
    if message.author.id not in messages:
      messages[message.author.id] = []
    messages[message.author.id].append((content_length,message.created_at))
    if len(messages[message.author.id]) > 2:
      messages[message.author.id].pop(0)
    heat,time = calc_message(messages[message.author.id])

    # Predict next
    heat_next, time_next = calc_message([messages[message.author.id][-1],(1,message.created_at)])
    if heat_next > 20000 and heat < 20000:
      seconds_to_wait = calc_cooldown(messages[message.author.id][-1])
      await message.channel.send(f"**{message.author.mention}, you're about to exceed the heat limit!**\nWait ``{seconds_to_wait}``  seconds before sending a new message.",delete_after=seconds_to_wait)

    # Fire Handling
    if not message.author.guild_permissions.administrator and not message.author.is_timed_out():
      if heat > 20000: # Harmful message spam
        await message.delete()
        has_penalty.setdefault(message.author.id, False)
        if has_penalty[message.author.id]:
          has_penalty[message.author.id] = False
          duration = datetime.timedelta(hours=1)
          await message.author.timeout(duration)
          db.exchange(self.bot.user.id,message.author.id,db.get('economy','coins',message.author.id)//2)
          await broadcast(message=message,title='Heavy message spam punishment',content=f"**Now you've done it, {message.author.mention}. Half your coins. Gone.**\n\nThis happened due to you breaking an important rule twice. Do not spam messages in order to get coins. You have been timed out for an hour.\n*Your XP and your Level remain the same. Create a ticket <#{config.TICKET_CHANNEL}> for further questions.*")
        else:
          has_penalty[message.author.id] = True
          duration = datetime.timedelta(minutes=30)
          await message.author.timeout(duration)
          await message.channel.purge(limit=10, check=lambda msg: is_author(msg, message.author))
          await broadcast(message=message,title='Heavy message spam warning',content=f"**You exceeded the heat limit, {message.author.mention} ! **\nYou have been timed out for 30 Minutes.\nDon't spam messages in order to get coins.\n*Doing this again could lead to a big coin loss. If you feel like this was an error, click appeal*",view=AppealButton(channel=self.bot.get_channel(config.MOD_CHANNEL),original_message=message))
        return
      elif time and time < 0.5: # Non-harmful fast message spam
        await message.delete()
        warnings.setdefault(message.author.id, 0)
        warnings[message.author.id] += 1
        if warnings[message.author.id] == 6:
            warnings[message.author.id] = 0 
            duration = datetime.timedelta(minutes=10)
            await message.author.timeout(duration)
            await broadcast(message=message,title='Fast message spam punishment',content=f"**You got a 10 minute timeout for spamming, {message.author.mention}**",thumb_url='https://media1.tenor.com/m/frOjgVit9XIAAAAd/rrane-battal.gif')
        elif warnings[message.author.id] == 2:
            duration = datetime.timedelta(seconds=10)
            await message.author.timeout(duration)
            await broadcast(message=message,title='Fast message spam warning',content=f"**{message.author.mention}, you're way too fast!**\nSlow down a bit with your messages.",thumb_url='https://media1.tenor.com/m/mAz6MzVaXxYAAAAd/duck-gun.gif')
        return
      
      # rewarding system
      if content_length > 200:
        content_length = 200
      coins_new = content_length // 10
      if message.author.premium_since:
        coins_new = content_length // 8
      xp_new = content_length // 4
      user_id = message.author.id
      user_rank = db.get("economy","rank",user_id)
      user_xp = db.get("economy","xp",user_id)
      bank_balance = db.get('economy','coins',self.bot.user.id)
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
          await message.channel.send(f"**:tada: Congrats {message.author.mention}, You just reached <:level:1172820830812643389> `` Rank {user_rank+rank_new} `` !\n\nTIP:** *You can exchange coins earned by chatting in <#{config.SHOP_CHANNEL}>.\nEnjoy your stay!*")
          user_xp = 0
          xp_new = xp_new-15
      db.put("economy","rank",user_id,user_rank+rank_new)
      db.put("economy","xp",user_id,xp_new+user_xp)
      if bank_balance < coins_new:
        if not bank_balance == 0:
          db.exchange(user_id,self.bot.user.id,bank_balance)
          await message.channel.send('@everyone :megaphone: The Bank is empty!!! No more coin rewards!!! All items are on 50% Sale go go go buy now !!!')
        else:
          pass
      else:
        if bank_balance - coins_new < message.guild.member_count*100 and not bank_balance < message.guild.member_count*100:
          await message.channel.send('@everyone :megaphone: The bank is getting emptier... All items are on 75% Sale!!!')
        db.exchange(user_id,self.bot.user.id,coins_new)
  @commands.Cog.listener()
  async def on_member_join(self,member):
    current = db.get("economy","coins",self.bot.user.id)
    set("economy","coins",self.bot.user.id,current+500)

async def setup(bot):
  await bot.add_cog(Events(bot))