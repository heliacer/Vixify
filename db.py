import sqlite3
import json
import os
from typing import List, Tuple

BASE = {'economy':['user_id','coins','rank','xp'],'items':['user_id','data']}

class Datastruct:
  def __init__(self):
    self.table = type(self).__name__.lower()

  def put(self, user_id: int, data_id: int, value: int = 0):
    result = fetch(self.table, "data", user_id)
    data: List[Tuple[int, int]]
    new_item = (data_id, value)
    if result == 0:
      data = [new_item]
    else:
      data = json.loads(result)
      for idx, item in enumerate(data):
        if item[0] == data_id:
          data[idx] = new_item
          break
      else:
        data.append(new_item)
    store(self.table, 'data', user_id, json.dumps(data))

  def get(self, user_id: int, data_id: int = None) -> int:
    result = fetch(self.table, 'data', user_id)
    if result != 0:
      items: List[Tuple[int, int]] = json.loads(result)
      if data_id:
        for item in items:
          if item[0] == data_id:
            return int(item[1])
    return 0

  def getall(self, user_id: int) -> List[Tuple[int, int]]:
    result = fetch(self.table, 'data', user_id)
    if result != 0:
      return json.loads(result)
    return []

  def increase(self, user_id: int, data_id: int, step: int = 1):
    value = self.get(user_id, data_id)
    self.put(user_id, data_id, value + step)

  def decrease(self, user_id: int, data_id: int, step: int = 1):
    value = self.get(user_id, data_id)
    self.put(user_id, data_id, value - step)

class Items(Datastruct):
  def __init__(self):
    super().__init__()

class Events(Datastruct):
  def __init__(self):
    super().__init__()

# localise the data structs

items = Items()
events = Events()

# SQL functions
conn = sqlite3.connect('vix.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY,coins INTEGER,rank INTEGER,xp INTEGER);''')
for table in Datastruct.__subclasses__():
  c.execute(f'''CREATE TABLE IF NOT EXISTS {table.__name__.lower()} (user_id INTEGER PRIMARY KEY, data TEXT);''')
conn.commit()

def init(value: int,id: int):
  c.execute('''INSERT OR IGNORE INTO economy (user_id, coins) VALUES (?, ?);''', (id, value))
  conn.commit()

def tablehasdata(table):
  c.execute(f'SELECT * FROM {table}')
  return c.fetchone() != None

def truncate(table:str):
  '''
  Delete all data from a table
  '''
  if not table.isidentifier():
    raise ValueError(f"Invalid table name: {table}")
  c.execute(f'DELETE FROM {table}')
  conn.commit()

def fetch(table: str, value: str = None, user_id: int = None):
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

def store(table:str,value: str,user_id:int,data):
  c.execute(f'''INSERT OR IGNORE INTO {table} (user_id, {value}) VALUES (?, ?)''', (user_id, 1))
  c.execute(f"""UPDATE {table} SET {value} = ? WHERE user_id = ?""", (data, user_id))
  conn.commit()

def exchange(target,sender,value):
  '''
  Exchange coins between two users
  '''
  sender_balance = fetch('economy','coins',sender)
  if sender_balance < value:
      raise Exception('Insufficient funds')
  store('economy','coins',sender,sender_balance-value)
  target_balance = fetch('economy','coins',target)
  store('economy','coins',target,target_balance+value)

def board(value:str, count:int = None):
  '''
  List the top users by a certain value
  '''
  query = f"SELECT user_id, {value} FROM economy ORDER BY {value} DESC"
  if count is not None:
    query += f" LIMIT {count}"
  c.execute(query)
  return c.fetchall()


def load(data: dict):
  '''
  I have no clue if this still works 
  '''
  for table in data:
    for item in data[table]:
      for value in item[1:]:
        store(table, BASE[table][item.index(value)],item[0],value)