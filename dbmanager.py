import sqlite3

conn = sqlite3.connect('vix.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS economy (user_id TEXT PRIMARY KEY,coins INTEGER,rank INTEGER,xp INTEGER);''')
c.execute('''CREATE TABLE IF NOT EXISTS items (user_id TEXT PRIMARY KEY, json_data TEXT);''')
conn.commit()

def check_reset(value: int,id: int):
    c.execute('''INSERT OR IGNORE INTO economy (user_id, coins) VALUES (?, ?);''', (str(id), value))
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


def exchange(target,sender,amount):
    sender_balance = get('economy','coins',sender)
    if sender_balance < amount:
        raise Exception('Insufficient funds')
    set('economy','coins',sender,sender_balance-amount)
    target_balance = get('economy','coins',target)
    set('economy','coins',target,target_balance+amount)

def set(table:str,value: str,user_id:int,data):
    c.execute(f'''INSERT OR IGNORE INTO {table} (user_id, {value}) VALUES (?, ?)''', (user_id, 1))
    c.execute(f"""UPDATE {table} SET {value} = ? WHERE user_id = ?""", (data, user_id))
    conn.commit()

def board(value:str,count:int,):
    c.execute(f'''SELECT user_id, {value} FROM economy ORDER BY {value} DESC LIMIT {count}''')
    return c.fetchall()
    