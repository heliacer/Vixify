import db
from discord.ext import commands
import discord
import config

class Admin(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  def isme():
    async def predicate(ctx):
        return ctx.author.id in config.ADMIN
    return commands.check(predicate)
  
  @commands.command()
  @isme()
  async def status(self, ctx, status):
    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.custom,name = " ",state = status.replace("_"," ")))
    await ctx.send(f"**<:confirm:1175396326272409670> Task executed.**", delete_after=10)

  @commands.command()
  @isme()
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
  @isme()
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

  @commands.command()
  @isme()
  async def items(self, ctx, operation, member: discord.Member, item_id = None, value = None):
    try:
      if operation == 'put':
        db.items.put(member.id,item_id,value)
        message = f"**<:confirm:1175396326272409670> Task executed.**"
      elif operation == 'get':
        result = db.items.get(member.id,item_id)
        message = f"``{result}``" 
      elif operation == 'increase':
        db.items.increase(member.id,item_id,int(value))
        message = f"**<:confirm:1175396326272409670> Task executed.**"
      elif operation == 'decrease':
        db.items.decrease(member.id,item_id,int(value))
        message = f"**<:confirm:1175396326272409670> Task executed.**"
      else:
        message = f"**<:questionable:1175393148294414347> Task does not exist.**"
    except Exception as e:
      message = f'**<:remove:1175005705422512218> Task failed.**\n```fix\n{e}```'
    await ctx.send(message,delete_after = 20)

async def setup(bot):
    await bot.add_cog(Admin(bot))
