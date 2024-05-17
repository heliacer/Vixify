import sqlite3
import json
import discord
from typing import List, Dict

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
    
  def get(user_id: int,item_id: int = None):
    result = get('items','json_data',user_id)
    if result != 0:
      items: list = json.loads(result)
      if item_id:
        return items.get(item_id)
      return items
    return []
  
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
        exchange(winner[0],interaction.client.user.id,pot/len(self.winners))
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