import chess
import discord
from PIL import Image
from core.ui import GameCheckoutGUI
from typing import Union
import asyncio
import io
from discord import ui

async def start(interaction: discord.Interaction,players:list):
  board = chess.Board()
  embed = discord.Embed()
  file = get_binary_board(board=board)
  embed.set_image(url="attachment://board.png")
  embed.set_author(name='Chess Gambling Session',icon_url='https://cdn-icons-png.flaticon.com/128/4960/4960287.png')
  pot = sum(item[1] for item in players)
  embed.set_footer(text=f'Total Pot: {pot}')
  await interaction.channel.send(content=f"`◻️ White `<@{players[0][0]}>'s turn!",embed=embed,view=ChessGameUI(board=board,players=players,current_player=players[0],color='white'),file=file)

def move_piece(move:str,board: chess.Board):
  try:
    move = chess.Move.from_uci(move)
    if move in board.legal_moves:
      board.push(move)
      return board
    elif move in board.pseudo_legal_moves:
      raise chess.IllegalMoveError('pseudo')
    else:
      raise chess.IllegalMoveError
  except chess.InvalidMoveError as error:
    raise chess.InvalidMoveError(error)

def get_piece_name(board: chess.Board,uci_name):
  try:
    return chess.piece_name(board.piece_at(chess.SQUARE_NAMES.index(uci_name)).piece_type)
  except Exception:
    return None


class SubmitUCIMove(ui.Modal,title='Chess Move'):
  def __init__(self,board,players: list,current_player,color):
    super().__init__(timeout=None)
    self.board = board
    self.players = players
    self.current_player = current_player
    self.color = 'white'
    if color == 'white':
      self.color = 'black'

  move = ui.TextInput(label='Your UCI Move. e.g e2e4.',style=discord.TextStyle.short)

  async def on_submit(self, interaction: discord.Interaction):
    move = interaction.data['components'][0]['components'][0]['value']
    moved_piece = get_piece_name(self.board,move[:2])
    try:
      board =  move_piece(move,self.board)
      embed = discord.Embed(description=f'{interaction.user.mention} moved {moved_piece.capitalize()} from ` {move[:2]} ` to ` {move[2:]} `')
      next_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]
      file = get_binary_board(board=board)
      embed.set_author(name='Chess Gambling Session',icon_url='https://cdn-icons-png.flaticon.com/128/4960/4960287.png')
      pot = sum(item[1] for item in self.players)
      embed.set_footer(text=f'Total Pot: {pot}')
      await interaction.response.defer()
      await interaction.delete_original_response()
      if board.is_check() and not board.is_checkmate():
        embed.description += '\n***Check!***'
      outcome = board.outcome()
      if outcome:
          embed.set_thumbnail(url="attachment://board.png")
          embed.description += f'\n***{outcome.termination.name.lower().capitalize()}!***\n**Total moves:** ` {len(board.move_stack)} `'
          print(outcome.termination.value)
          winner = self.current_player if outcome.termination.value == 2 else None
          print(winner)
          win_message = await interaction.channel.send(content=f'🏆 {self.current_player[0]} The Session has ended!\n**Winner:** ` {"◻️ White" if self.color == "black" else "◼️ Black"} ` {interaction.user.mention}',embed=embed,view=GameCheckoutGUI(self.players,[winner],10),file=file)
          for i in range(10):
            await asyncio.sleep(1)
            try:
              await win_message.edit(view=GameCheckoutGUI(self.players,[winner],9-i))
            except discord.NotFound:
              break
          delayed = GameCheckoutGUI(self.players, [winner],0)
          await delayed.payout(message=win_message)
          return
      embed.set_image(url="attachment://board.png")
      await interaction.channel.send(content=f"`{'◼️' if self.color == 'black' else '◻️' + self.color.capitalize()} `<@{next_player[0]}>'s turn!",embed=embed,view=ChessGameUI(board,self.players,next_player,self.color),file=file)
    except chess.InvalidMoveError:
      await interaction.response.send_message(f'` {move} ` is not a valid move. Try again.',ephemeral=True)
    except chess.IllegalMoveError as error:
      if error == 'pseudo':
        await interaction.response.send_message(f'` {move[:2]} ` to ` {move[2:]} ` is a Pseudo legal move. Your King is in check.',ephemeral=True)
      else:
        await interaction.response.send_message(f'` {move[:2]} ` to ` {move[2:]} ` is a Illegal move. Try again.',ephemeral=True)

class ChessGameUI(ui.View):
  def __init__(self,board:chess.Board,players:list,current_player,color):
    super().__init__(timeout=None)
    self.board = board
    self.players = players
    self.current_player = current_player
    self.color = color

  @ui.button(label='Make UCI Move',emoji='<:touch:1216394992512274482>')
  async def makemove(self,interaction: discord.Interaction,button):
    if interaction.user.id == self.current_player[0]:
      await interaction.response.send_modal(SubmitUCIMove(self.board,self.players,self.current_player,self.color))
    else:
      await interaction.response.send_message("It's not your turn!",ephemeral=True)

  @ui.button(label='UCI Help',emoji='<:questionable:1175393148294414347>')
  async def help(self,interaction: discord.Interaction,button):
    embed = discord.Embed(title='Game GUI Instructions',description="1. **Move Your Pieces:**\n - Use chessboard coordinates to specify moves. Each square has a unique label, like e2 or g7.\n - To move a piece, type the starting square (e.g., e2) followed by the destination square (e.g., e4). No spaces or special characters needed.\n2. **Example Moves:**\n - Move a pawn from e2 to e4: `e2e4`\n - Move a knight from g1 to f3: `g1f3`\n3. **Finding Coordinates:**\n - Look at the edges of the board for letter and number labels.\n - The letters (a-h) represent columns, and the numbers (1-8) represent rows.\n\nEnjoy playing chess!")
    await interaction.response.send_message(embed=embed,ephemeral=True)

  @ui.button(label='Give Up',emoji='<:sandclock:1203261564291911680>')
  async def giveup(self,interaction: discord.Interaction,button):
    next_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]
    winner = self.current_player if interaction.user.id != self.current_player[0] else next_player
    embed = discord.Embed(description=f'**{interaction.user.mention} gave up, hat a shame.**\n**Total moves:** ` {len(self.board.move_stack)} `\n<@{winner[0]}> wins all the coins.')
    await interaction.response.defer()
    await interaction.delete_original_response()
    win_message = await interaction.channel.send(embed=embed,view=GameCheckoutGUI(self.players,[next_player],10))
    for i in range(10):
      await asyncio.sleep(1)
      try:
        await win_message.edit(view=GameCheckoutGUI(self.players,[next_player],9-i))
      except discord.NotFound:
        break
    delayed = GameCheckoutGUI(self.players, [next_player],0)
    await delayed.payout(message=win_message)
    
@staticmethod
def get_binary_board(board) -> discord.File:
    size = (500, 500)

    with io.BytesIO() as binary:
        board = Generator.generate(board).resize(size, Image.Resampling.LANCZOS)
        board.save(binary, "PNG"); binary.seek(0)
        return discord.File(fp = binary, filename = "board.png")

class Generator:
  layout = [
      [ chess.A8, chess.B8, chess.C8, chess.D8, chess.E8, chess.F8, chess.G8, chess.H8 ],
      [ chess.A7, chess.B7, chess.C7, chess.D7, chess.E7, chess.F7, chess.G7, chess.H7 ],
      [ chess.A6, chess.B6, chess.C6, chess.D6, chess.E6, chess.F6, chess.G6, chess.H6 ],
      [ chess.A5, chess.B5, chess.C5, chess.D5, chess.E5, chess.F5, chess.G5, chess.H5 ],
      [ chess.A4, chess.B4, chess.C4, chess.D4, chess.E4, chess.F4, chess.G4, chess.H4 ],
      [ chess.A3, chess.B3, chess.C3, chess.D3, chess.E3, chess.F3, chess.G3, chess.H3 ],
      [ chess.A2, chess.B2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2 ],
      [ chess.A1, chess.B1, chess.C1, chess.D1, chess.E1, chess.F1, chess.G1, chess.H1 ]
  ]

  coordinates = [ 25, 109, 194, 279, 363, 448, 531, 616 ]

  @staticmethod
  def generate(board: chess.BaseBoard) -> Image:
      chessboard = Image.open("assets/chess/chessboard.png")

      for y, Y in enumerate(Generator.coordinates):
          for x, X in enumerate(Generator.coordinates):
              piece = board.piece_at(Generator.layout[y][x])

              if piece is not None:
                  path = Generator.path(piece)
              else: continue

              piece = Image.open(path).convert("RGBA")
              
              chessboard.paste(piece, (X, Y), piece)

      return chessboard

  @staticmethod
  def path(piece: chess.Piece) -> Union[str, None]:
      path = "assets/chess/"

      if piece.color == chess.WHITE: path += "white/"
      if piece.color == chess.BLACK: path += "black/"

      if piece.piece_type == chess.PAWN: path += "pawn.png"
      if piece.piece_type == chess.KNIGHT: path += "knight.png"
      if piece.piece_type == chess.BISHOP: path += "bishop.png"
      if piece.piece_type == chess.ROOK: path += "rook.png"
      if piece.piece_type == chess.QUEEN: path += "queen.png"
      if piece.piece_type == chess.KING: path += "king.png"

      return path