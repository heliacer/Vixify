import json
import sqlite3
from typing import List, Union

class Row:
    """
    Base class for all `Row` objects serialized into a `Column`.
    """

    def __init__(self, id: int, values: List[int]) -> None:
        self.id = id
        self.values = values

    def __eq__(self, other: 'Row') -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"Row {self.id} {self.values}"

    @staticmethod
    def unload(data: str) -> List['Row']:
        """
        Unpacks the JSON string from the database into a list of `Row` objects.

        Args:
            data (str): JSON string containing the serialized `Row` data.

        Returns:
            List[Row]: A list of `Row` objects.
        """
        return [Row(item[0], item[1]) for item in json.loads(data)]

    @staticmethod
    def pack(data: List['Row']) -> str:
        """
        Packs the list of `Row` objects into a JSON string for database storage.

        Args:
            data (List[Row]): A list of `Row` objects to be serialized.

        Returns:
            str: A JSON string representing the serialized `Row` objects.
        """
        return json.dumps([[item.id, item.values] for item in data])


class Column:
    """
    Base class for all columns in the database.
    Each column represents a TEXT field in the database table.
    """

    def __init__(self):
        self.table = type(self).__name__.lower()

    def put(self, user_id: int, row_id: int, value: int = 0, key: int = 0) -> None:
        """
        Put a value into a column.

        Args:
            user_id (int): The ID of the user.
            row_id (int): The ID of the row.
            value (int, optional): The value to put. Defaults to 0.
            key (int, optional): The index in the row values to update. Defaults to 0.
        """
        result = fetch(self.table, "data", user_id)
        if result == 0:
            column = [Row(row_id, [value])]
        else:
            column = Row.unload(result)
            for row in column:
                if row.id == row_id:
                    row.values[key] = value
                    break
            else:
                column.append(Row(row_id, [value]))
        store(self.table, 'data', user_id, Row.pack(column))

    def get(self, user_id: int, row_id: int = None, key: int = 0) -> int:
        """
        Get a value from a column.

        Args:
            user_id (int): The ID of the user.
            row_id (int, optional): The ID of the row. Defaults to None.
            key (int, optional): The index in the row values to retrieve. Defaults to 0.

        Returns:
            int: The value at the specified position, or 0 if not found.
        """
        result = fetch(self.table, 'data', user_id)
        if result != 0:
            items = Row.unload(result)
            if row_id is not None:
                return next((item.values[key] for item in items if item.id == row_id), 0)
        return 0

    def getall(self, user_id: int) -> List[Row]:
        """
        Get all values from a column.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[Row]: A list of `Row` objects.
        """
        result = fetch(self.table, 'data', user_id)
        if result != 0:
            return Row.unload(result)
        return []

    def increase(self, user_id: int, row_id: int, step: int = 1, key: int = 0) -> None:
        """
        Increase a value in a column row.

        Args:
            user_id (int): The ID of the user.
            row_id (int): The ID of the row.
            step (int, optional): The increment step. Defaults to 1.
            key (int, optional): The index in the row values to increase. Defaults to 0.
        """
        value = self.get(user_id, row_id, key)
        self.put(user_id, row_id, value + step, key)

    def decrease(self, user_id: int, row_id: int, step: int = 1, key: int = 0) -> None:
        """
        Decrease a value in a column row.

        Args:
            user_id (int): The ID of the user.
            row_id (int): The ID of the row.
            step (int, optional): The decrement step. Defaults to 1.
            key (int, optional): The index in the row values to decrease. Defaults to 0.
        """
        value = self.get(user_id, row_id, key)
        self.put(user_id, row_id, value - step, key)


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

items = Items()
mails = Mails()
usage = Usage()

# SQL connection & cursor
conn = sqlite3.connect('vix.db')
c = conn.cursor()

# Initialize the database tables
c.execute('''CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY, coins INTEGER, rank INTEGER, xp INTEGER);''')
for table in Column.__subclasses__():
    c.execute(f'''CREATE TABLE IF NOT EXISTS {table.__name__.lower()} (user_id INTEGER PRIMARY KEY, data TEXT);''')
conn.commit()

# SQL functions
def init(value: int, id: int) -> None:
    """
    Initialize a user with a starting value.

    Args:
        value (int): The initial value (e.g., coins).
        id (int): The user ID.
    """
    c.execute('''INSERT OR IGNORE INTO economy (user_id, coins) VALUES (?, ?);''', (id, value))
    conn.commit()

def tablehasdata(table: str) -> bool:
    """
    Check if a table has any data.

    Args:
        table (str): The name of the table.

    Returns:
        bool: True if the table has data, False otherwise.
    """
    c.execute(f'SELECT * FROM {table}')
    return c.fetchone() is not None

def deletedata(table: str) -> None:
    """
    Delete all data from a table.

    Args:
        table (str): The name of the table.

    Raises:
        ValueError: If the table name is invalid.
    """
    if not table.isidentifier():
        raise ValueError(f"Invalid table name: {table}")
    c.execute(f'DELETE FROM {table}')
    conn.commit()

def fetch(table: str, value: str = None, user_id: int = None) -> Union[int, str, list]:
    """
    Fetch data from a table.

    Args:
        table (str): The name of the table.
        value (str, optional): The specific column value to fetch. Defaults to None.
        user_id (int, optional): The user ID to filter by. Defaults to None.

    Returns:
        Union[int, str, list]: The fetched data.
    """
    query = f"SELECT {value} FROM {table}" if value else f"SELECT * FROM {table}"
    query += f" WHERE user_id = ?" if user_id else ""
    c.execute(query, (user_id,) if user_id else ())
    if value and user_id:
        fromdb = c.fetchone()
        return fromdb[0] if fromdb and fromdb[0] else 0
    return c.fetchall()

def store(table: str, value: str, user_id: int, data: Union[int, str]) -> None:
    """
    Store data in a table.

    Args:
        table (str): The name of the table.
        value (str): The column to store the data in.
        user_id (int): The user ID.
        data (Union[int, str]): The data to store.
    """
    c.execute(f'''INSERT OR IGNORE INTO {table} (user_id, {value}) VALUES (?, ?)''', (user_id, 1))
    c.execute(f"""UPDATE {table} SET {value} = ? WHERE user_id = ?""", (data, user_id))
    conn.commit()

def exchange(target: int, sender: int, value: int) -> None:
    """
    Exchange coins between two users.

    Args:
        target (int): The ID of the target user.
        sender (int): The ID of the sender user.
        value (int): The amount of coins to exchange.

    Raises:
        Exception: If the sender has insufficient funds.
    """
    sender_balance = fetch('economy', 'coins', sender)
    if sender_balance < value:
        raise Exception('Insufficient funds')
    store('economy', 'coins', sender, sender_balance - value)
    target_balance = fetch('economy', 'coins', target)
    store('economy', 'coins', target, target_balance + value)

def board(value: str, count: int = None) -> list:
    """
    List the top users by a certain value.

    Args:
        value (str): The value to sort by.
        count (int, optional): The number of top users to list. Defaults to None.

    Returns:
        list: A list of tuples containing user ID and the specified value.
    """
    query = f"SELECT user_id, {value} FROM economy ORDER BY {value} DESC"
    if count is not None:
        query += f" LIMIT {count}"
    c.execute(query)
    return c.fetchall()