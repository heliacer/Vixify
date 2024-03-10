from dbmanager import set,get
from discord.ext import commands
import discord
import config

class Admin(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  def isme():
    async def predicate(ctx):
        return ctx.author.id in config.isme
    return commands.check(predicate)
  
  @commands.command()
  @isme()
  async def set(self, ctx, table, value, member: discord.Member, *, data):
    tryjson = data[1:-1]
    if tryjson.startswith("{"):
      data = tryjson
    try:
      set(table, value, member.id, data)
      message = f"```sql\nUPDATE {table} SET {value} = {data} WHERE user_id = {member.id}\n```"
    except Exception as e:
      message = f'```fix\n{e}```'
    await ctx.send(message, delete_after=10)

  @commands.command()
  @isme()
  async def get(self, ctx, table, value=None, member: discord.Member = None):
    user_id = None
    if member:
       user_id = member.id
    try:
      result = get(table, value, user_id)
      message = f"```fix\n{result}```"
    except Exception as e:
      message = f'```fix\n{e}```'
    await ctx.send(message, delete_after=20)

async def setup(bot):
    await bot.add_cog(Admin(bot))
