import sqlite3
import json
from typing import List

BASE = {'economy':['user_id','coins','rank','xp'],'items':['user_id','data']}

class BaseItem:
    '''
    Base class for all items, which serialize and deserialize to and from the database
    '''
    def __init__(self, id: int, data: List[int]) -> None:
        self.id = id
        self.data = data
        

    def __eq__(self, value: 'BaseItem') -> bool:
      return self.id == value.id

    def __repr__(self) -> str:
        return f"BaseItem {self.id} ({self.value})"
    
    @staticmethod
    def unload(data: str) -> List['BaseItem']:
        '''
        Unpacks the JSON string from database into a list of `BaseItem` objects
        '''
        return [BaseItem(item[0], item[1]) for item in json.loads(data)]
  
    @staticmethod
    def pack(data: List['BaseItem']) -> str:
        '''
        Packs the list of `BaseItem` objects into a JSON string for database storage
        '''
        return json.dumps([[item.id, item.data] for item in data])

class Column:
  '''
  Base class for all data columns, which use the same methods to interact with the database
  '''
  def __init__(self):
    self.table = type(self).__name__.lower()

  def put(self, user_id: int, data_id: int, value: int = 0,key: int = 0) -> None:
    '''
    Put a value into a Column
    TODO this has some bugs 
    '''
    result = fetch(self.table, "data", user_id)
    baseitems: List[BaseItem]
    new_item = BaseItem(data_id, [value])
    if result == 0:
      baseitems: List[BaseItem] = [new_item]
    else:
      baseitems = BaseItem.unload(result)
      for item in baseitems:
        if item.id == data_id:
          item.data[key] = value
      else:
        baseitems.append(new_item)
    store(self.table, 'data', user_id, BaseItem.pack(baseitems))

  def get(self, user_id: int, data_id: int = None,key: int = 0) -> int:
      '''
      Get a value `int` from a Column
      '''
      result = fetch(self.table, 'data', user_id)
      if result != 0:
          items = BaseItem.unload(result)
          return next((item.data[key] for item in items if item.id == data_id), 0) if data_id is not None else 0
      return 0

  def getall(self, user_id: int) -> List[BaseItem]:
    '''
    Get all values `BaseItem` from a `Column`
    '''
    result = fetch(self.table, 'data', user_id)
    if result != 0:
      return BaseItem.unload(result)
    return []

  def increase(self, user_id: int, data_id: int, step: int = 1,key: int = 0) -> None:
    '''
    Increase a `int` value in a `Column` `BaseItem`
    '''
    value = self.get(user_id, data_id,key)
    self.put(user_id, data_id, value + step,key)

  def decrease(self, user_id: int, data_id: int, step: int = 1,key: int = 0) -> None:
    '''
    Decrease a `int` value in a `Column` `BaseItem`
    '''
    value = self.get(user_id, data_id,key)
    self.put(user_id, data_id, value - step,key)

# Columns which inherit from the Column class  

class Items(Column):
  def __init__(self):
    super().__init__()

class Mails(Column):
  def __init__(self):
    super().__init__()

class Usage(Column):
  def __init__(self):
    super().__init__()

# SQL connection & cursor
conn = sqlite3.connect('vix.db')
c = conn.cursor()

# localise the data structs
items = Items()
mails = Mails()
usage = Usage()

c.execute('''CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY,coins INTEGER,rank INTEGER,xp INTEGER);''')
for table in Column.__subclasses__():
  c.execute(f'''CREATE TABLE IF NOT EXISTS {table.__name__.lower()} (user_id INTEGER PRIMARY KEY, data TEXT);''')
conn.commit()

# SQL functions
def init(value: int,id: int) -> None:
  c.execute('''INSERT OR IGNORE INTO economy (user_id, coins) VALUES (?, ?);''', (id, value))
  conn.commit()

def tablehasdata(table) -> bool:
  c.execute(f'SELECT * FROM {table}')
  return c.fetchone() != None

def deletedata(table:str) -> None:
  '''
  Delete all data from a table
  '''
  if not table.isidentifier():
    raise ValueError(f"Invalid table name: {table}")
  c.execute(f'DELETE FROM {table}')
  conn.commit()

def fetch(table: str, value: str = None, user_id: int = None) -> int | str:
  '''
  Fetch data from a table directly
  '''
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

def store(table:str,value: str,user_id:int,data) -> None:
  '''
  Store data in a table directly
  '''
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