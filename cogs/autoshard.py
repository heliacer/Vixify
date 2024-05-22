import discord
import config
import db
from discord.ext import commands
from core.misc import messages, warnings, has_penalty, ranks
from core.misc import broadcast, calc_cooldown, calc_message, stripCodeBlocks, isauthor, format_seconds
import datetime
from discord import app_commands
import traceback
from core.plugins import Plugin
import io

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
        await ctx.send(f'<:confirm:1175396326272409670> Heat cleared for {member.mention}')
        
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

        # Ignore code blocks
        message.content = stripCodeBlocks(message.content)

        # Add heat, calculate stuff
        content_length = len(message.content)
        if message.author.id not in messages:
            messages[message.author.id] = []
        messages[message.author.id].append((content_length, message.created_at))
        if len(messages[message.author.id]) > 2:
            messages[message.author.id].pop(0)
        heat, time = calc_message(messages[message.author.id])

        # Predict next
        heat_next, time_next = calc_message([messages[message.author.id][-1], (1, message.created_at)])
        if heat_next > 20000 and heat < 20000:
            seconds_to_wait = calc_cooldown(messages[message.author.id][-1])
            await message.channel.send(
                f"**{message.author.mention}, you're about to exceed the heat limit!**\nWait ``{seconds_to_wait}``  seconds before sending a new message.",
                delete_after=seconds_to_wait)

        # Fire Handling
        if not message.author.guild_permissions.administrator and not message.author.is_timed_out():
            if heat > 20000:  # Harmful message spam
                await message.delete()
                has_penalty.setdefault(message.author.id, False)
                if has_penalty[message.author.id]:
                    has_penalty[message.author.id] = False
                    duration = datetime.timedelta(hours=1)
                    await message.author.timeout(duration)
                    db.exchange(self.bot.user.id, message.author.id,
                                db.users.get('coins', message.author.id) // 2)
                    await broadcast(message=message, title='Heavy message spam punishment',
                                    content=f"**Now you've done it, {message.author.mention}. Half your coins. Gone.**\n\nThis happened due to you breaking an important rule twice. Do not spam messages in order to get coins. You have been timed out for an hour.\n*Your XP and your Level remain the same. Create a ticket <#{config.TICKET_CHANNEL}> for further questions.*")
                else:
                    has_penalty[message.author.id] = True
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
                warnings.setdefault(message.author.id, 0)
                warnings[message.author.id] += 1
                if warnings[message.author.id] == 6:
                    warnings[message.author.id] = 0
                    duration = datetime.timedelta(minutes=10)
                    await message.author.timeout(duration)
                    await broadcast(message=message, title='Fast message spam punishment',
                                    content=f"**You got a 10 minute timeout for spamming, {message.author.mention}**",
                                    thumb_url='https://media1.tenor.com/m/frOjgVit9XIAAAAd/rrane-battal.gif')
                elif warnings[message.author.id] == 2:
                    duration = datetime.timedelta(seconds=10)
                    await message.author.timeout(duration)
                    await broadcast(message=message, title='Fast message spam warning',
                                    content=f"**{message.author.mention}, you're way too fast!**\nSlow down a bit with your messages.",
                                    thumb_url='https://media1.tenor.com/m/mAz6MzVaXxYAAAAd/duck-gun.gif')
                return

        # Rewarding system
        if content_length > 200:
            content_length = 200
        coins_new = content_length // 10
        if message.author.premium_since:
            coins_new = content_length // 8
        xp_new = content_length // 4
        user_id = message.author.id
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
                    f"**Congrats {message.author.mention}, You just reached <:level:1172820830812643389> `` Rank {user_rank + rank_new} ``{msg}**",
                    allowed_mentions=None)
        else:
            if user_xp + xp_new > 15:
                rank_new += 1
                await message.channel.send(
                    f"**:tada: Congrats {message.author.mention}, You just reached <:level:1172820830812643389> `` Rank {user_rank + rank_new} `` !\n\nTIP:** *You can exchange coins earned by chatting in <#{config.SHOP_CHANNEL}>.\nEnjoy your stay!*")
                user_xp = 0
                xp_new = xp_new - 15
        db.users.inc('rank',user_id,rank_new)
        db.users.inc("xp",user_id,xp_new )
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
        db.users.inc('coins',self.bot.user.id,500)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, (commands.CheckFailure, commands.CommandNotFound)):
            return
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description=f'***<:sandclock:1203261564291911680> This command is on cooldown. Try again after {format_seconds(error.retry_after)}***')
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound, commands.BadArgument, commands.MissingPermissions, commands.BotMissingPermissions)):
            embed = discord.Embed(description=f'**<:err:1203262608929722480> {error}**')
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandError):
            embed = discord.Embed(description=f'**<:err:1203262608929722480> {error}**')
            await ctx.send(embed=embed)
        else:
            exception = traceback.format_exception(type(error), error, error.__traceback__)
            file = discord.File(filename="error.log", fp=io.BytesIO(''.join(exception).encode()))
            ErrorEmbed = discord.Embed(description=f'**<:err:1203262608929722480> There was an internal error.**')
            ErrorEmbed.set_footer(text=str(error))
            await ctx.send(embed=ErrorEmbed, file=file)

async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        CooldownEmbed = discord.Embed(
            description=f'***<:sandclock:1203261564291911680> This command is on cooldown. Try again after {format_seconds(error.retry_after)}***')
        await interaction.response.send_message(embed=CooldownEmbed, ephemeral=True)
    else:
        exception = traceback.format_exception(type(error), error, error.__traceback__)
        file = discord.File(filename="error.log", fp=io.BytesIO(''.join(exception).encode()))
        ErrorEmbed = discord.Embed(description=f'**<:err:1203262608929722480> There was an internal error.**')
        ErrorEmbed.set_footer(text=str(error))
        await interaction.response.send_message(embed=ErrorEmbed, file=file)

async def setup(bot: commands.AutoShardedBot):
    bot.tree.on_error = on_app_command_error 
    await bot.add_cog(Events(bot))
