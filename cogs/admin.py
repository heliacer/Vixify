from discord.ext import commands
import discord
import db
import os
import config
from core.plugins import Plugin

CONFIRM_MESSAGE = "**<:confirm:1175396326272409670> Task executed.**"
CONFIRM_EMBED = discord.Embed(description=CONFIRM_MESSAGE)

class Admin(Plugin):
  @commands.command()
  @commands.has_permissions(administrator=True)
  async def cleartable(self, ctx, table, syntax=None):
    if not db.tablehasdata(table) or syntax == "force":
      db.deletedata(table)
      message = CONFIRM_MESSAGE
    else:
      message = f"**<:remove:1175005705422512218> Table has data. Use `force` to clear table.**"
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed, delete_after=10)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def dbinit(self, ctx):
    guild = self.bot.get_guild(config.GUILD)
    db.init(guild.member_count * 200,self.bot.user.id)
    embed = discord.Embed(description=CONFIRM_MESSAGE)
    await ctx.send(embed=embed, delete_after=10)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def setstatus(self, ctx, status):
    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.custom,name = " ",state = status.replace("_"," ")))
    await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

  @commands.command()
  @commands.has_permissions(administrator=True)
  async def store(self, ctx, table, value, member: discord.Member, *, data):
    tryjson = data[1:-1]
    if tryjson.startswith("{"):
      data = tryjson
    try:
      db.store(table, value, member.id, data)
      message = CONFIRM_MESSAGE
    except Exception as e:
      message = f'**<:remove:1175005705422512218> Task failed.**\n```fix\n{e}```'
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed, delete_after=10)

  @commands.command()
  async def fetch(self, ctx, table, value=None, member: discord.Member = None):
    user_id = None
    if member:
       user_id = member.id
    try:
      result = db.fetch(table, value, user_id)
      if isinstance(result, list):
        if not result:
          result = 'No data found.'
        else:
          result = '\n'.join(map(str, result))
      message = f"```\n{result}\n```"
      await ctx.send(message, delete_after=20)
    except Exception as e:
      message = f'**<:remove:1175005705422512218> Task failed.**\n```fix\n{e}```'
      embed = discord.Embed(description=message)
      await ctx.send(embed=embed, delete_after=20)

  @commands.group()
  @commands.has_permissions(administrator=True)
  async def items(self, ctx: commands.Context):
      if ctx.invoked_subcommand is None:
        embed = "**<:questionable:1175393148294414347> Item task does not exist.**"
        await ctx.send(embed=embed, delete_after=10)

  @items.command()
  async def put(self, ctx, member: discord.Member, item_id: int, value = 1):
      db.items.put(member.id, item_id, value)
      await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

  @items.command()
  async def get(self, ctx, member: discord.Member, item_id: int = None):
      if item_id:
        result = db.items.get(member.id, item_id)
      else:
        result = db.items.getall(member.id)
      await ctx.send(f"```\n{result}\n```", delete_after=20)

  @items.command()
  async def increase(self, ctx, member: discord.Member, item_id: int, value: int):
      db.items.increase(member.id, item_id, value)
      await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

  @items.command()
  async def decrease(self, ctx, member: discord.Member, item_id: int, value: int):
      db.items.decrease(member.id, item_id, value)
      await ctx.send(embed=CONFIRM_EMBED, delete_after=10)

async def setup(bot):
    await bot.add_cog(Admin(bot))
