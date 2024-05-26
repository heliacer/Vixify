from discord.ext import commands
from discord import app_commands
import discord
import db
import config
from core.plugins import Plugin
from core.emojis import *
from core.items import getItems,getItemByID

CONFIRM_MESSAGE = f"**{CONFIRM_EMOJI} Task executed.**"
CONFIRM_EMBED = discord.Embed(description=CONFIRM_MESSAGE)

class Admin(Plugin):
  @app_commands.command(name = "giveuser",description="Admin tools to modify user rank, coins & xp")
  @app_commands.describe(member="The member you want to give to.")
  @app_commands.describe(amount="The amount you want to give. Not all items are shown here, search for the item you want to give.")
  @app_commands.describe(type="The type of value you want to give.")
  @app_commands.choices(type=[app_commands.Choice(name=value.capitalize(), value=value) for value in ['coins','xp','rank']])
  @app_commands.checks.has_permissions(administrator=True)
  async def giveuser(self, interaction: discord.Interaction,type: str, member: discord.Member, amount: int):
    db.users.increment(type,member.id,amount)
    embed = discord.Embed(description=f'**{CONFIRM_EMOJI} Gave ` {amount} {type.capitalize()} ` to {member.mention}**')
    await interaction.response.send_message(embed=embed,ephemeral=True)

  async def admin_panel_items(self, interaction: discord.Interaction, current: str):
    items = getItems()
    return [
        app_commands.Choice(name=item.name, value=str(item.id))
        for item in items if current.lower() in item.name.lower()
    ][:25]

  @app_commands.command(name = "giveitem",description="Admin tools to modify users items")
  @app_commands.describe(member="The member you want to give to.")
  @app_commands.describe(item="The item you want to give.")
  @app_commands.describe(amount="The amount you want to give.")
  @app_commands.autocomplete(item=admin_panel_items)
  @app_commands.checks.has_permissions(administrator=True)
  async def giveitem(self, interaction: discord.Interaction, member: discord.Member, item: str, amount: int = 1):
    fullitem = getItemByID(int(item))
    db.items.increment(member.id, fullitem.id, amount)
    embed = discord.Embed(description=f'{CONFIRM_EMOJI} Gave *{amount:,}x* {fullitem.emoji} **{fullitem.name}** to {member.mention}')
    await interaction.response.send_message(embed=embed)

  @commands.command(description="Clears a table in the database.")
  @commands.has_permissions(administrator=True)
  async def cleartable(self, ctx, table, syntax=None):
    if not db.fetch(f'SELECT * FROM {table}') or syntax == "force":
      db.commit(f'DELETE * FROM {table}')
      message = CONFIRM_MESSAGE
    else:
      message = f"**{REMOVE_EMOJI} Table has data. Use `force` to clear table.**"
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed, delete_after=10)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def dbinit(self, ctx):
    guild = self.bot.get_guild(config.GUILD)
    db.users.set('coins',self.bot.user.id,guild.member_count * 200)
    embed = discord.Embed(description=CONFIRM_MESSAGE)
    await ctx.send(embed=embed, delete_after=10)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def setstatus(self, ctx, status):
    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.custom,name = " ",state = status.replace("_"," ")))
    await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

  @commands.group()
  @commands.has_permissions(administrator=True)
  async def items(self, ctx: commands.Context):
      if ctx.invoked_subcommand is None:
        embed = f"**{QUESTION_EMOJI} Item task does not exist.**"
        await ctx.send(embed=embed, delete_after=10)

  @items.command()
  async def set(self, ctx, member: discord.Member, item_id: int, value = 1):
      db.items.set(member.id, item_id, value)
      await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

  @items.command()
  async def get(self, ctx, member: discord.Member, item_id: int = None):
      if item_id:
        result = db.items.get(member.id, item_id)
      else:
        result = db.items.all(member.id)
      await ctx.send(f"```\n{result}\n```", delete_after=20)

  @items.command()
  async def put(self, ctx, member: discord.Member, item_id: int, value: int):
      db.items.increment(member.id, item_id, value)
      await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

async def setup(bot):
    await bot.add_cog(Admin(bot))
