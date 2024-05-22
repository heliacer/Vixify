import sqlite3
from typing import List

conn = sqlite3.connect("vix.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  coins INTEGER DEFAULT 0,
  xp INTEGER DEFAULT 0,
  rank INTEGER DEFAULT 0
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS items (
  item_id INTEGER,
  user_id INTEGER,
  amount INTEGER DEFAULT 0,
  timestamp INTEGER DEFAULT 0,
  PRIMARY KEY (item_id, user_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);
''')

class BaseItem:
  def __init__(self, item_id: int,user_id:int, amount: int = 0, timestamp: int = 0):
    self.id = item_id
    self.amount = amount
    self.timestamp = timestamp
  def __repr__(self) -> str:
    return f"BaseItem | ID {self.id} | Amount {self.amount} | Timestamp {self.timestamp}"
  
class BaseUser:
  def __init__(self, user_id: int, coins: int, xp: int, rank: int):
    self.id = user_id
    self.coins = coins
    self.xp = xp
    self.rank = rank
  def __repr__(self) -> str:
    return f"BaseUser | ID {self.id} | Coins {self.coins} | XP {self.xp} | Rank {self.rank}"

class Users:
  def all(self,user_id: int) -> BaseUser | None:
    """
    Returns a list of all fields in a user's row
    """
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) 
    result = cursor.fetchone()
    return BaseUser(*result) if result else None
  
  def get(self,field: str,user_id: int) -> int:
    cursor.execute(f"SELECT {field} FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0
  
  def set(self, field: str,user_id: int, value: int | str) -> None:
    """
    Sets a field in a user's row, if the field does not exist it will be created.
    """
    cursor.execute(f'''
    INSERT INTO users (user_id, {field})
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET {field} = excluded.{field}
    ''', (user_id, value))
    conn.commit()
    
  def inc(self, field: str, user_id: int, step: int = 1) -> None:
      """
      Increments a field in a user's row, if the field does not exist it will be created.
      This does not overwrite the field, it adds the step to the current value.
      """
      if not isinstance(step, int):
          raise TypeError("Step must be an integer")

      query = f'''
      INSERT INTO users (user_id, {field})
      VALUES (?, ?)
      ON CONFLICT(user_id) DO UPDATE SET {field} = {field} + excluded.{field}
      '''
      cursor.execute(query, (user_id, step))
      conn.commit()


class Items:
  def all(self,user_id: int) -> List[BaseItem]:
    """
    Returns a list of all items in a user's items
    """
    cursor.execute("SELECT * FROM items WHERE user_id = ?", (user_id,))
    result = cursor.fetchall()
    return [BaseItem(*row) for row in result]

  def get(self,user_id: int, item_id: int) -> int | str | None:
    """
    Gets the amount of an item in a user's items
    """
    cursor.execute("SELECT amount FROM items WHERE user_id = ? AND item_id = ?", (user_id, item_id))
    result = cursor.fetchone()
    return result[0] if result else None
  
  def set(self,user_id: int, item_id: int, amount: int) -> None:
    """
    Sets the amount of an item in a user's items, if the item does not exist it will be created.
    """
    cursor.execute(f'''
    INSERT INTO items (user_id, item_id, amount)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, item_id) DO UPDATE SET amount = excluded.amount
    ''', (user_id, item_id, amount))
    conn.commit()

  def inc(self,user_id: int, item_id: int, step: int = 1) -> None:
    '''
    Increments the amount of an item in a user's items, if the item does not exist it will be created.
    This does not overwrite the amount, it adds the step to the current amount
    '''
    cursor.execute(f'''
    INSERT INTO items (user_id, item_id, amount)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, item_id) DO UPDATE SET amount = amount + excluded.amount
    ''', (user_id, item_id, step))
    conn.commit()

def commit(query: str, *args) -> None:
  '''
  Modifies the database with a custom query, commiting the changes
  '''
  cursor.execute(query, args)
  conn.commit()

def fetch(query: str, *args) -> str | int | List[int | str] | None:
  '''
  Fetches data from the database with a custom query
  '''
  cursor.execute(query, args)
  result = cursor.fetchone()
  return result[0] if result else None
  
def wipe(user_id: int) -> None:
  '''
  Wipes a user from the database, usually performed when a user leaves the server
  '''
  cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
  cursor.execute("DELETE FROM items WHERE user_id = ?", (user_id,))
  conn.commit()

users = Users()
items = Items()

def exchange(target: int, sender: int, value: int) -> None:
  '''
  Exchange coins between two users
  '''
  sender_balance = users.get('coins',sender)
  if sender_balance < value:
    raise Exception('Insufficient funds')
  users.inc('coins',sender,-value)
  users.inc('coins',target,value)

def board(value: str, count: int = None) -> List[int]:
  """
  List the top users by a certain value.
  """
  query = f"SELECT user_id, {value} FROM users ORDER BY {value} DESC"
  if count:
    query += f" LIMIT {count}"
  cursor.execute(query)
  return cursor.fetchall()
