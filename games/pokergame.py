import discord
import asyncio
import random
from poker import *


async def start(interaction: discord.Interaction,players:list):
  shuffleembed = discord.Embed(description='**Shuffling the deck...**')
  shuffleembed.set_author(name='Poker Gambling Session',icon_url='https://cdn-icons-png.flaticon.com/128/8043/8043648.png')
  startmessage = await interaction.channel.send(embed=shuffleembed)
  await asyncio.sleep(3)
  deck = list(Card)
  random.shuffle(deck)
  players = [(tpl[0], tpl[1], [deck.pop() for i in range(5)]) for tpl in players]
  await LoadTable(startmessage,players,deck)


async def LoadTable(message: discord.Message,players,deck):
  print(players)
  await message.edit(content=players)


# TODO: use poker api to get card images https://www.deckofcardsapi.com/ ( epic nevix idea )