import discord
import config
import db
from discord.ext import commands
import datetime
import time
from discord import app_commands
import traceback
from core.misc import messages, warnings, has_penalty, ranks
from core.misc import broadcast, calc_cooldown, calc_message, stripCodeBlocks, isauthor
from core.plugins import Plugin
from core.emojis import *
import io

class ConfirmDeclineButtons(discord.ui.View):
  def __init__(self,original_message: discord.Message):
    super().__init__(timeout=None)
    self.original_message = original_message

  @discord.ui.button(label="Accept",emoji=CONFIRM_EMOJI)
  async def accept(self,interaction: discord.Interaction,button: discord.ui.Button):
    await interaction.response.edit_message(view=None)
    await broadcast(message=self.original_message,content=f"{PARTYHORN_EMOJI} Your Appeal was accepted by {interaction.user.mention}. Happy you're back!\nPlease excuse any mistakes we have made. We try to constantly improve.",thumb_url='https://media1.tenor.com/m/KhtKI4EkuR0AAAAd/seal-silly.gif')
    await self.original_message.author.timeout(None)
    await self.original_message.channel.send(f"Recovered message by {self.original_message.author.mention}:\n\n{self.original_message.content}")
    await interaction.channel.send(f'{PASSION_EMOJI} Thanks for your feedback and hard work, {interaction.user.mention}')

  @discord.ui.button(label="Decline",emoji=REMOVE_EMOJI)
  async def decline(self,interaction: discord.Interaction,button: discord.ui.Button):
    await interaction.response.edit_message(view=None)
    await broadcast(message=self.original_message,content=f"{REMOVE_EMOJI} Your Appeal was declined by {interaction.user.mention}. We're sorry.",thumb_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSVdxamPXtGCZdAwZSGvZIz95afqYpIEYYLiQNA-v5WZwkXTirx')
    await interaction.channel.send(f'{PASSION_EMOJI} Thanks for your feedback and hard work, {interaction.user.mention}')

class AppealButton(discord.ui.View):
  def __init__(self,channel: discord.TextChannel,original_message: discord.Message):
    super().__init__(timeout=None)
    self.channel = channel
    self.original_message = original_message

  @discord.ui.button(label="Appeal",emoji=SEND_EMOJI)
  async def appeal(self,interaction: discord.Interaction,button: discord.ui.Button):
    update_embed = discord.Embed(title='Long Message spam appeal',description=f'{self.original_message.author.mention} sent a message in {self.original_message.channel.mention} and would like to appeal:\n\n>>> {self.original_message.content}')
    await self.channel.send(embed=update_embed,view=ConfirmDeclineButtons(self.original_message))
    button.disabled = True
    await interaction.response.edit_message(view=self)
    await interaction.channel.send(f'{CONFIRM_EMOJI} Appeal sent. Please wait until it has been revieved.')



class Events(Plugin):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        super().__init__(bot=bot)
  
    @commands.command(name='clearheat')
    @commands.has_permissions(administrator=True)
    async def clearheat(self, ctx: commands.Context, member: discord.Member):
        messages[member.id] = []
        warnings[member.id] = []
        has_penalty[member.id] = False
        await ctx.send(f'{CONFIRM_EMOJI} Heat cleared for {member.mention}')
        
    @commands.command(name=f"ping")
    async def ping(self, ctx: commands.Context):

      msg = await ctx.send('Pong!')
      await msg.edit(content='Pong! ``{0}ms``'.format(round(self.bot.latency, 1))) 

    @commands.Cog.listener() # this needs the most refactoring
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return

        user_id = message.author.id
        # Ignore code blocks
        message.content = stripCodeBlocks(message.content)

        # Add heat, calculate stuff
        content_length = len(message.content)
        if user_id not in messages:
            messages[user_id] = []
        messages[user_id].append((content_length, message.created_at))
        if len(messages[user_id]) > 2:
            messages[user_id].pop(0)
        heat, time = calc_message(messages[user_id])

        # Predict next
        heat_next, time_next = calc_message([messages[user_id][-1], (1, message.created_at)])
        if heat_next > 20000 and heat < 20000:
            seconds_to_wait = calc_cooldown(messages[user_id][-1])
            await message.channel.send(
                f"**{message.author.mention}, you're about to exceed the heat limit!**\nWait ``{seconds_to_wait}``  seconds before sending a new message.",
                delete_after=seconds_to_wait)

        # Fire Handling
        if not message.author.guild_permissions.administrator and not message.author.is_timed_out():
            if heat > 20000:  # Harmful message spam
                await message.delete()
                has_penalty.setdefault(user_id, False)
                if has_penalty[user_id]:
                    has_penalty[user_id] = False
                    duration = datetime.timedelta(hours=1)
                    await message.author.timeout(duration)
                    db.exchange(self.bot.user.id, user_id,
                                db.users.get('coins', user_id) // 2)
                    await broadcast(message=message, title='Heavy message spam punishment',
                                    content=f"**Now you've done it, {message.author.mention}. Half your coins. Gone.**\n\nThis happened due to you breaking an important rule twice. Do not spam messages in order to get coins. You have been timed out for an hour.\n*Your XP and your Level remain the same. Create a ticket <#{config.TICKET_CHANNEL}> for further questions.*")
                else:
                    has_penalty[user_id] = True
                    duration = datetime.timedelta(minutes=30)
                    await message.author.timeout(duration)
                    await message.channel.purge(limit=10, check=lambda msg: isauthor(msg, message.author))
                    await broadcast(message=message, title='Heavy message spam warning',
                                    content=f"**You exceeded the heat limit, {message.author.mention} ! **\nYou have been timed out for 30 Minutes.\nDon't spam messages in order to get coins.\n*Doing this again could lead to a big coin loss. If you feel like this was an error, click appeal*",
                                    view=AppealButton(channel=self.bot.get_channel(config.MOD_CHANNEL),
                                                      original_message=message))
                return
            elif time and time < 0.5:  # Non-harmful fast message spam
                await message.delete()
                warnings.setdefault(user_id, 0)
                warnings[user_id] += 1
                if warnings[user_id] == 6:
                    warnings[user_id] = 0
                    duration = datetime.timedelta(minutes=10)
                    await message.author.timeout(duration)
                    await broadcast(message=message, title='Fast message spam punishment',
                                    content=f"**You got a 10 minute timeout for spamming, {message.author.mention}**",
                                    thumb_url='https://media1.tenor.com/m/frOjgVit9XIAAAAd/rrane-battal.gif')
                elif warnings[user_id] == 2:
                    duration = datetime.timedelta(seconds=10)
                    await message.author.timeout(duration)
                    await broadcast(message=message, title='Fast message spam warning',
                                    content=f"**{message.author.mention}, you're way too fast!**\nSlow down a bit with your messages.",
                                    thumb_url='https://media1.tenor.com/m/mAz6MzVaXxYAAAAd/duck-gun.gif')
                return

        # Rewarding system
        if content_length > 200:
            content_length = 200

        coins_new: int = content_length // 10
        xp_new = content_length // 4

        # Pendant 1.5x Boost for Nitro
        if message.author.premium_since:
            coins_new = content_length // 7.5

        # Adjust for temporary boosts
        now_time = datetime.datetime.now().timestamp()
        xp_boost_timestamp = db.items.get(user_id,4001,'timestamp')
        coins_boost_timestamp = db.items.get(user_id,4002,'timestamp')

        if now_time < xp_boost_timestamp if xp_boost_timestamp else False:
            xp_new = content_length // 2
        if now_time < coins_boost_timestamp if coins_boost_timestamp else False:
            coins_new = content_length // 5

        user_rank = db.users.get('rank',user_id)
        user_xp = db.users.get('xp',user_id)
        bank_balance = db.users.get('coins',self.bot.user.id)
        rank_new = 0
        if user_rank != 0:
            if user_xp + xp_new >= (user_rank) * 120:
                while user_xp + xp_new >= (user_rank) * 120:
                    rank_new += 1
                    msg = ""
                    for key, value in ranks:
                        if value["rank"] == user_rank + rank_new:
                            role = message.guild.get_role(value["roleid"])
                            if role:
                                await message.author.add_roles(role)
                                msg = f"\n You just gathered `` {role.name} ``"
                    xp_new = xp_new - ((user_rank) * 120 - 120)
                    user_xp = 0
                await message.channel.send(
                    f"**Congrats {message.author.mention}, You just reached {LEVEL_EMOJI} `` Rank {user_rank + rank_new} ``{msg}**",
                    allowed_mentions=None)
        else:
            if user_xp + xp_new > 15:
                rank_new += 1
                await message.channel.send(
                    f"**:tada: Congrats {message.author.mention}, You just reached {LEVEL_EMOJI} `` Rank {user_rank + rank_new} `` !\n\nTIP:** *You can exchange coins earned by chatting in <#{config.SHOP_CHANNEL}>.\nEnjoy your stay!*")
                user_xp = 0
                xp_new = xp_new - 15

        db.users.increment('rank',user_id,rank_new)
        db.users.increment("xp",user_id,xp_new )

        if bank_balance < coins_new:
            if not bank_balance == 0:
                db.exchange(user_id, self.bot.user.id, bank_balance)
                await message.channel.send(
                    '@everyone :megaphone: The Bank is empty!!! No more coin rewards!!! All items are on 50% Sale go go go buy now !!!')
        else:
            if bank_balance - coins_new < message.guild.member_count * 100 and not bank_balance < message.guild.member_count * 100:
                await message.channel.send(
                    '@everyone :megaphone: The bank is getting emptier... All items are on 75% Sale!!!')
            db.exchange(user_id, self.bot.user.id, coins_new)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db.users.increment('coins',self.bot.user.id,500)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, (commands.CheckFailure, commands.CommandNotFound)):
            return
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description=f'***{SANDCLOCK_EMOJI} This command is on cooldown. Try again <t:{int(time.time() + error.retry_after)}:R> ***')
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, (commands.MissingPermissions, commands.CheckFailure)):
            embed = discord.Embed(description=f'**{ERR_EMOJI} {error}**')
            await ctx.send(embed=embed)
        else:
            exception = traceback.format_exception(type(error), error, error.__traceback__)
            file = discord.File(filename="error.log", fp=io.BytesIO(''.join(exception).encode()))
            ErrorEmbed = discord.Embed(description=f'**{ERR_EMOJI} There was an internal error.**')
            ErrorEmbed.set_footer(text=str(error))
            await ctx.send(embed=ErrorEmbed, file=file)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # TODO : append embed on the existing interaction passed, don't override current embed
        pass
        
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = discord.Embed(description=f'***{SANDCLOCK_EMOJI} This command is on cooldown. Try again <t:{int(time.time() + error.retry_after)}:R> ***')
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif isinstance(error, (app_commands.MissingPermissions,app_commands.CheckFailure)):
        embed = discord.Embed(description=f'**{ERR_EMOJI} {error}**')
        await interaction.response.send_message(embed=embed)
    else:
        exception = traceback.format_exception(type(error), error, error.__traceback__)
        file = discord.File(filename="error.log", fp=io.BytesIO(''.join(exception).encode()))
        ErrorEmbed = discord.Embed(description=f'**{ERR_EMOJI} There was an internal error.**')
        ErrorEmbed.set_footer(text=str(error))
        await interaction.response.send_message(embed=ErrorEmbed, file=file)

async def setup(bot: commands.AutoShardedBot):
    bot.tree.on_error = on_app_command_error 
    await bot.add_cog(Events(bot))
