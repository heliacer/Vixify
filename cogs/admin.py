import config
from dbmanager import set,get
from discord.ext import commands


class Admin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def isme(ctx) -> bool:
    return ctx.author.id in config.isme

  @commands.command(name = "set")
  @commands.check(isme)
  async def set(self,ctx,table, value, memberID,*,data):
    tryjson = data[1:-1]
    if tryjson.startswith("{"):
      data = tryjson
    try:
      set(table,value,memberID,data)
      message = f"```sql\nUPDATE {table} SET {value} = {data} WHERE user_id = {memberID}\n```"
    except Exception as e:
      message = f'```fix\n{e}```'
    await ctx.send(message,delete_after=10)

  @commands.command(name = "get")
  @commands.check(isme)
  async def get(self,ctx,table, value=None, memberID=None):
    try:
      result = get(table,value,memberID)
      message = f"```fix\n{result}```"
    except Exception as e:
      message = f'```fix\n{e}```'
    await ctx.send(message,delete_after=20)

async def setup(bot):
  await bot.add_cog(Admin(bot))
