from discord.ext import commands
import discord
import db
import os
import config
from core.plugins import Plugin
from core.predicate import admin


class Admin(Plugin):
  @commands.command()
  @admin()
  async def init(self, ctx,syntax: str = None):
    if not os.path.exists('vix.db') or syntax =="-f":
      guild = self.bot.get_guild(config.GUILD)
      db.init(guild.member_count * 200,self.bot.user.id)
      await ctx.send(f"**<:confirm:1175396326272409670> Task executed.**", delete_after=10)
    else:
      await ctx.send(f"**<:err:1203262608929722480> Database already exists. Use -f syntax to forcefully overwrite data.**", delete_after=10)

  @commands.command()
  @admin()
  async def status(self, ctx, status):
    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.custom,name = " ",state = status.replace("_"," ")))
    await ctx.send(f"**<:confirm:1175396326272409670> Task executed.**", delete_after=10)

  @commands.command()
  @admin()
  async def set(self, ctx, table, value, member: discord.Member, *, data):
    tryjson = data[1:-1]
    if tryjson.startswith("{"):
      data = tryjson
    try:
      db.put(table, value, member.id, data)
      message = f"**<:confirm:1175396326272409670> Task executed.**"
    except Exception as e:
      message = f'**<:remove:1175005705422512218> Task failed.**\n```fix\n{e}```'
    await ctx.send(message, delete_after=10)

  @commands.command()
  @admin()
  async def get(self, ctx, table, value=None, member: discord.Member = None):
    user_id = None
    if member:
       user_id = member.id
    try:
      result = db.get(table, value, user_id)
      if isinstance(result, list):
        result = '\n'.join(map(str, result))
      message = f"``{result}``"
    except Exception as e:
      message = f'**<:remove:1175005705422512218> Task failed.**\n```fix\n{e}```'
    await ctx.send(message, delete_after=20)

  @commands.group()
  @admin()
  async def items(self, ctx: commands.Context):
      if ctx.invoked_subcommand is None:
          await ctx.send("**<:questionable:1175393148294414347> Item task does not exist.**", delete_after=10)

  @items.command()
  async def put(self, ctx, member: discord.Member, item_id, value):
      db.items.put(member.id, item_id, value)
      await ctx.send("**<:confirm:1175396326272409670> Task executed.**", delete_after=10)

  @items.command()
  async def get(self, ctx, member: discord.Member, item_id):
      result = db.items.get(member.id, item_id)
      await ctx.send(f"``{result}``", delete_after=20)

  @items.command()
  async def increase(self, ctx, member: discord.Member, item_id, value: int):
      db.items.increase(member.id, item_id, value)
      await ctx.send("**<:confirm:1175396326272409670> Task executed.**", delete_after=10)

  @items.command()
  async def decrease(self, ctx, member: discord.Member, item_id, value: int):
      db.items.decrease(member.id, item_id, value)
      await ctx.send("**<:confirm:1175396326272409670> Task executed.**", delete_after=10)

async def setup(bot):
    await bot.add_cog(Admin(bot))
