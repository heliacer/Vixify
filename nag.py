import chess

board = chess.Board()

piece = chess.piece_name(board.piece_at(chess.SQUARE_NAMES.index('e2')).piece_type)
print(piece)