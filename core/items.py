import json
from typing import List
import discord
import random
import db
from datetime import datetime
from core.emojis import *

class Item:
    def __init__(self, name: str, description: str, id: int,price: int= 0, type: str= 'misc',emoji: discord.Emoji= '',stack: int = None,rarity: int=1,buyable: bool=True):
        self.name = name
        self.description = description
        self.price = price
        self.id = id
        self.type = type
        self.rarity = rarity
        self.emoji = emoji
        self.stack = stack if stack else 1 if type in ['boost','role','command'] else 0
        self.buyable = buyable

    def __eq__(self, value: 'Item') -> bool:
      return self.id == value.id

    def __repr__(self):
        return f"Item {self.name} ({self.id})"

def loadItemsFromJSON(file_path) -> List[Item]:
    with open(file_path, 'r') as file:
        items_data = json.load(file)
        items = [Item(**item) for item in items_data]
    return items

ITEMS = loadItemsFromJSON("assets/items.json")

def getItems() -> List[Item]:
    return ITEMS

def getItemsByType(types: List[str],items: List[Item] = ITEMS) -> List[Item]:
    return [item for item in items if item.type in types]

def getItemByID(id: int,items: List[Item] = ITEMS) -> Item:
  for item in items:
    if item.id == id:
      return item
    
def getNextItemPrice(user: discord.Member,sale: int,items: List[Item] = ITEMS) -> int:
    user_roles: List[int] = [role.id for role in user.roles]
    sorted_features: List[Item] = sorted(items, key=lambda item: item.id)
    next_item = next((item for item in sorted_features if item.id not in user_roles), None)
    return next_item.price * sale if next_item else 0

def getRandomItemByRarity(rarity: int,items: List[Item] = ITEMS) -> Item:
    '''
    `rarity` 1 being common and 5 being legendary, returns a random item based on the rarity
    ## Example
    ```python
    item = getRandomItemByRarity(3)
    print(item.rarity)
    ```
    This returns an item with rarity 3 in most cases, but can return rarities 2, 4, 1, and 5 with decreasing probabilities.
    '''
    weights = {
        rarity: 60,
        rarity - 1: 30 if rarity > 1 else 0,
        rarity + 1: 30 if rarity < 5 else 0,
        rarity - 2: 10 if rarity > 2 else 0,
        rarity + 2: 10 if rarity < 4 else 0,
    }
    weighted_items: List[Item] = []

    for item in items:
        weight = weights.get(item.rarity, 0)
        weighted_items.extend([item] * weight)
    if not weighted_items:
        raise ValueError(f"No items found with rarity {rarity}")
    
    return random.choice(weighted_items)

def getItemBoard(baseitems: List[db.BaseItem]) -> str:
    item_categories = {'streak': [], 'boost': [], 'role': [], 'command': [], 'utility': [], 'misc': []}
    board: str = ''
    total: int = 0
       
    for baseitem in baseitems:
        total += baseitem.amount
        item = getItemByID(baseitem.id)
        type = item.type if item.type in item_categories else 'misc'
        itemname = item.name if item.emoji == '' else f"{item.emoji} {item.name}"
        
        if type in ['role', 'command']:
            item_categories[type].append(f"**{itemname}**\n")
        elif type == 'streak':
            item_categories[type].append(f"**{item.name}**: {FIREUP_EMOJI} ` {baseitem.amount} `\n")
        elif type == 'boost':
            delta = datetime.fromtimestamp(baseitem.timestamp) - datetime.now()
            if delta.total_seconds() > 0:
                item_categories[type].append(f"**{itemname}** expires <t:{int(baseitem.timestamp)}:R> \n")
        else:
            item_categories[type].append(f"*{baseitem.amount}x* **{itemname}**\n")
    
    for category, items_list in item_categories.items():
        if items_list:
            category_label = category.capitalize()
            board += f"` {category_label} `\n{''.join(items_list)}\n"

    board += f"**Total:** ` {total} items `\n\n"
    return board

def useItem(user_id: int, item: Item,amount: int = 1, duration: int = 0) -> discord.Embed:
    embed = discord.Embed(description=f"You have used a **{item.emoji} {item.name}**!")
    match item.id:
      case 3001:
        db.items.increment(user_id, 3001, -amount)
        db.users.increment('xp',user_id, 100*amount)
        embed.description += f"\nYou gained {LEVEL_EMOJI}` {100*amount} XP `!"
      case _:
        embed.description += "\nThis item has no effect (yet)"
    return embed