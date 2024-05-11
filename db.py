import sqlite3
import json
import discord
import config
from typing import List

conn = sqlite3.connect('vix.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY,coins INTEGER,rank INTEGER,xp INTEGER);''')
c.execute('''CREATE TABLE IF NOT EXISTS items (user_id INTEGER PRIMARY KEY, json_data TEXT);''')
conn.commit()

def refresh(value: int,id: int):
  c.execute('''INSERT OR IGNORE INTO economy (user_id, coins) VALUES (?, ?);''', (id, value))
  conn.commit()

def drop(table:str):
  c.execute(f'DROP TABLE {table}')
  conn.commit()

def get(table: str, value: str = None, user_id: int = None):
  query = f"SELECT {value} FROM {table}" if value else f"SELECT * FROM {table}"
  query += f" WHERE user_id = ?" if user_id else ""
  c.execute(query, (user_id,) if user_id else ())
  if value and user_id:
    fromdb = c.fetchone()
    if fromdb:
        if fromdb[0]: 
            result = fromdb[0]
        else:
            result = 0     
    else:
        result = 0
  else:
    result = c.fetchall()
  return result

def put(table:str,value: str,user_id:int,data):
  c.execute(f'''INSERT OR IGNORE INTO {table} (user_id, {value}) VALUES (?, ?)''', (user_id, 1))
  c.execute(f"""UPDATE {table} SET {value} = ? WHERE user_id = ?""", (data, user_id))
  conn.commit()

def exchange(target,sender,amount):
  sender_balance = get('economy','coins',sender)
  if sender_balance < amount:
      raise Exception('Insufficient funds')
  put('economy','coins',sender,sender_balance-amount)
  target_balance = get('economy','coins',target)
  put('economy','coins',target,target_balance+amount)

def board(value:str, count:int = None):
  query = f"SELECT user_id, {value} FROM economy ORDER BY {value} DESC"
  if count is not None:
    query += f" LIMIT {count}"
  c.execute(query)
  return c.fetchall()

class items():
  def put(user_id :int,item_id: int,amount: int = 0):
    result = get("items","json_data",user_id)
    if result == 0:
      data = {}
    else:
      data = json.loads(result)
    data[item_id] = amount
    put('items','json_data',user_id,json.dumps(data))
    
  def get(user_id: int,item_id: int):
    result = get('items','json_data',user_id)
    if result != 0:
      data = json.loads(result).get(item_id,0)
      return data
    return result
  
  def increase(user_id: int,item_id: int,step: int):
    amount = items.get(user_id,item_id)
    amount += step
    items.put(user_id,items,amount)

  def decrease(user_id: int,item_id: int,step: int):
    amount = items.get(user_id,item_id)
    amount -= step
    items.put(user_id,items,amount)

def load(data: dict):
  base = {'economy':['user_id','coins','rank','xp'],'items':['user_id','json_data']}
  for table in data:
    for item in data[table]:
      for value in item[1:]:
        put(table, base[table][item.index(value)],item[0],value)

class GameCheckoutGUI(discord.ui.View):
  def __init__(self,players: list,winners: List[List[int]],seconds):
    super().__init__(timeout=None)
    self.players = players
    self.winners = winners
    payout_button = discord.ui.Button(label=f'Proceed to payout ({seconds})',style=discord.ButtonStyle.blurple,emoji='<:checkout:1175007951669436446>')
    payout_button.callback = self.payout
    self.add_item(payout_button)

  async def payout(self,interaction: discord.Interaction = None,message: discord.Message = None):
    quote = "\n\n>>> 99% of gamblers quit before they win big. Don't be a bitch.\nJust take another loan and win all your money back, that's how I do it. Remember: *«There are no losers, just quitters»*"
    if self.winners:
      pot = sum(item[1] for item in self.players)
      embed = discord.Embed(description='')
      for winner in self.winners:
        exchange(winner[0],config.bot_id,pot/len(self.winners))
        embed.description += f"<@{winner[0]}> got paid <:coins:1172819933093179443>` {pot} Coins `{quote}\n"
    else:
      embed = discord.Embed(description=f'**All gamblers recieve their money back due to a draw.**{quote}')
    embed.set_author(name='Gambling Checkout',icon_url='https://cdn-icons-png.flaticon.com/128/8580/8580823.png')
    if interaction:
      await interaction.message.delete()
      await interaction.channel.send(embed=embed)
    if message:
      print(message)
      await message.delete()
      await message.channel.send(embed=embed)


if __name__ == "__main__":
  load({'economy':[(1135585805939789834, 30627), 
 (955187087911555152, 1631, 16, -1068), 
 (960499267997429780, 862, 7, -403), 
 (753626747303362611, 3082, 12, -870), 
 (1022602321370296371, 194, 4, -229), 
 (748846312278982736, 207, 4, -225), 
 (751347251300794398, 831, 3, 241), 
 (1113965765184454736, 11, 1, 17), 
 (1020995268159754321, 191, 3, 70), 
 (759830243447275562, 315, 3, 234), 
 (680730865051238482, 206, 3, 82), 
 (825000454269829152, 8, 1, -3), 
 (259807482619101197, 52, 2, 18), 
 (756533079547314296, 4, 0, 12), 
 (1109866667867131924, 87, 2, 105), 
 (831404387624157225, 53, 2, 15), 
 (298886885210587136, 1152, 5, 570), 
 (1040118920276873266, 494, 5, -293), 
 (879709400678412328, 11, 1, 11), 
 (1057104290600189972, 8, 1, 2), 
 (731391223692132444, 14, 1, 25), 
 (251831918973157376, 224, 8, 113), 
 (792701022426234890, 181, 1, 67), 
 (1157384184210407514, 0, 0, 0), 
 (635834352172793877, 3, 0, 10), 
 (1183120117995941982, 2, 0, 5), 
 (895927318822932480, 46, 1, 105), 
 (667073342661984256, 161, 2, 173), 
 (630800927900827649, 3, 0, 8)],'items': [(753626747303362611, '{1001: 3}'), (955187087911555152, '{1001: 15}')]
})