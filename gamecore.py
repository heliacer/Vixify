import random
from typing import Optional
import discord
import functools
from dbmanager import get

from games.chessgame import start_chess, ChessGameUI

games = {'chess': (2,2)}

class SubmitKey(discord.ui.Modal, title = 'Join private gambling session'):
  key = discord.ui.TextInput(label='Key',style=discord.TextStyle.short)
  def __init__(self,interaction: discord.Interaction,game,players: list,key,submitter):
    super().__init__(timeout=None)
    self.interaction = interaction
    self.game = game
    self.players = players
    self.key = key
    self.submitter = submitter
    
  async def on_submit(self, interaction: discord.Interaction):
    if str(self.key) == interaction.data['components'][0]['components'][0]['value']:
        self.players.append((interaction.user.id,0))
        await interaction.response.defer()
        await LobbyPage(self.interaction,self.game,self.players,self.key)
    else:
      await interaction.response.send_message('Incorrect key. Try again.',ephemeral=True)


class PlaceBet(discord.ui.Modal, title='Place bet'):
  amount = discord.ui.TextInput(label='Amount',style=discord.TextStyle.short)
  def __init__(self,interaction: discord.Interaction,game,players: list,key):
    super().__init__(timeout=None)
    self.interaction = interaction
    self.game = game
    self.players = players
    self.key = key
  
  async def on_submit(self, interaction: discord.Interaction):
    bet = interaction.data['components'][0]['components'][0]['value']
    if bet.isnumeric():
      amount = int(bet)
      if amount in range(50,1500):
        user_balance = get('economy','coins',interaction.user.id)
        if user_balance >= amount:
          await LobbyPage(self.interaction,self.game,[(x, y) if x != interaction.user.id else (x, amount) for x, y in self.players],self.key)
          await interaction.response.send_message("Your Bet was placed. You can change it by setting your Bet again.",ephemeral=True)
        else:
          await interaction.response.send_message("You have insufficient funds mafaka. :angry:",ephemeral=True)
      else:
        await interaction.response.send_message('Your Bet must be at least <:coins:1172819933093179443> ` 50 - 1500 Coins `',ephemeral=True)
    else:
      await interaction.response.send_message('Your Bet must be a valid number.',ephemeral=True)

class LobbyPanel(discord.ui.View):
  def __init__(self,interaction: discord.Interaction,game,players: list,key):
    super().__init__(timeout=None)
    self.interaction = interaction
    self.game = game
    self.players = players
    self.key = key
    if self.key:
      button_gk = discord.ui.Button(label='Get Key',custom_id='LobbyPanel.GetKey',row=0)
      button_pub = discord.ui.Button(label='Set Public',custom_id='LobbyPanel.SetPublic',row=0)
      button_gk.callback = self.get_key
      button_pub.callback = functools.partial(self.toggle_mode, key=self.key)
      self.add_item(button_gk)
      self.add_item(button_pub)
    else:
      button_priv = discord.ui.Button(label='Set Private',custom_id='LobbyPanel.SetPrivate',row=0)
      button_priv.callback = functools.partial(self.toggle_mode, key=None)
      self.add_item(button_priv)
  
  async def get_key(self, interaction: discord.Interaction):
    if self.players[0][0] == interaction.user.id:
      await interaction.response.send_message(self.key,ephemeral=True)
    else:
      await interaction.response.send_message('Only the Host can get the code.\nAsk for the code so you can join!',ephemeral=True)

  async def toggle_mode(self,interaction: discord.Interaction, key):
    if self.players[0][0] == interaction.user.id:
      await interaction.response.defer()
      if key:
        await LobbyPage(self.interaction,self.game,self.players,None)
      else:
        await LobbyPage(self.interaction,self.game,self.players,random.randint(1000,9999))
    else:
      await interaction.response.send_message('Only the Host can toggle between public & private mode.',ephemeral=True)

  @discord.ui.button(label='Start Game',custom_id='LobbyPanel.Start',row=0)
  async def start_game(self,interaction: discord.Interaction,button: discord.ui.Button):
    if self.players[0][0] == interaction.user.id:
      await self.interaction.delete_original_response()
      if self.game == 'chess':
        board = start_chess()
        await interaction.response.defer()
        await interaction.channel.send(f'<@{self.players[0][0]}> turn!\n```\n{board}\n```',view=ChessGameUI(board,self.players,self.players[0][0]))
    else:
      await interaction.response.send_message('Only the Host can start the game.',ephemeral=True)

  @discord.ui.button(label='Join',custom_id='LobbyPanel.Join',row=1)
  async def join_game(self,interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id not in [player[0] for player in self.players]:
      if self.key:
        await interaction.response.send_modal(SubmitKey(self.interaction,self.game,self.players,self.key,interaction.user.id))
      else:
        self.players.append((interaction.user.id,0))
        await interaction.response.defer()
        await LobbyPage(self.interaction,self.game,self.players,self.key)
    else:
      await interaction.response.send_message('You already joined this game.',ephemeral=True)
  
  @discord.ui.button(label='leave',custom_id='LobbyPanel.Leave',row=1)
  async def leave_game(self,interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id == self.players[0][0]:
      await interaction.response.defer()
      await self.interaction.delete_original_response()
    elif interaction.user.id in [player[0] for player in self.players]:
      await interaction.response.defer()
      await LobbyPage(self.interaction,self.game,[tup for tup in self.players if tup[0] != interaction.user.id],self.key)
    else:
      await interaction.response.send_message("You haven't joined the game yet, mafaka.",ephemeral=True)

  @discord.ui.button(label='Place Bet',custom_id='LobbyPanel.PlaceBet',row=1)
  async def place_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id not in [player[0] for player in self.players]:
      await interaction.response.send_message("You haven't joined this game yet.",ephemeral=True)
    else:
      await interaction.response.send_modal(PlaceBet(self.interaction,self.game,self.players,self.key))

async def LobbyPage(interaction: discord.Interaction,game: str,players:list,key:int):
  playerslist  = "\n".join(f'<@{player[0]}> <:coins:1172819933093179443> ` {player[1]} Coins ` :crown:' if player[0] == players[0][0] else f'<@{player[0]}> <:coins:1172819933093179443> ` {player[1]} Coins `' for player in players)
  playermin = games[game][0]
  playermax = games[game][1]
  mode = '<:worldwide:1203760886842527855> ` Public `'
  if key:
    mode = '<:padlock:1178730730998734980> ` Private `'
  PageEmbed = discord.Embed(title=game.capitalize(), description=f'` {str(playermin) + "-" + str(playermax) if playermax != playermin else "Min " + str(playermin)} Players ` {mode}\n\n**Players Joined**\n{playerslist}\n\nTotal Bet: <:coins:1172819933093179443> ` {sum([player[1] for player in players])} Coins `')
  await interaction.edit_original_response(embed=PageEmbed,view=LobbyPanel(interaction,game,players,key))
  
class GameMenu(discord.ui.View):
  def __init__(self,key: int,host_id, host_bet: int):
    super().__init__(timeout=None)
    self.key = key
    self.host_id = host_id
    self.host_bet = host_bet

    options = [discord.SelectOption(label=name) for name, game in games.items()]
    gameselection = discord.ui.Select(custom_id="GameMenu.GameSelect",placeholder="Select a game",max_values=1,min_values=1,options=options)

    gameselection.callback = self.gameselect
    self.add_item(gameselection)

  async def gameselect(self,interaction: discord.Interaction):
    if interaction.user.id == self.host_id:
      game = interaction.data['values'][0]
      await interaction.response.defer()
      await LobbyPage(interaction,game,[(self.host_id,self.host_bet)],self.key)
    else:
      await interaction.response.send_message('Only the Host can choose the game.',ephemeral=True)
