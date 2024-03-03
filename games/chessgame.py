import chess
import chess.svg
from discord import ui

def start_chess():
  board = chess.Board()
  return board

def move_piece(move:str,board: chess.Board):
  try:
    move = chess.Move.from_uci(move)
    if move in board.legal_moves:
      board.push(move)
      return board
    else:
      return chess.IllegalMoveError
  except chess.InvalidMoveError as error:
    return error

class ChessGameUI(ui.View):
  def __init__(self,board:chess.Board,players,current_player):
    super().__init__(timeout=None)

# TODO: make Chessgameui work
