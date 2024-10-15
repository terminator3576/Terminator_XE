import chess
import time
import multiprocessing

def search_mate(board, depth, is_maximizing_player, time_limit, start_time):
    if time_limit and (time.time() - start_time >= time_limit):
        return None, None
    if board.is_checkmate():
        return 0, None
    if depth == 0 or board.is_game_over():
        return None, None

    best_mate_in = None
    best_move = None

    if is_maximizing_player:
        # Try to find the quickest mate for the current player
        for move in board.legal_moves:
            board.push(move)
            mate_in, _ = search_mate(board, depth - 1, False, time_limit, start_time)
            board.pop()

            if mate_in is not None:
                if best_mate_in is None or mate_in + 1 < best_mate_in:
                    best_mate_in = mate_in + 1
                    best_move = move

            # Time check after each move
            if time_limit and (time.time() - start_time >= time_limit):
                return None, None
    else:
        for move in board.legal_moves:
            board.push(move)
            mate_in, _ = search_mate(board, depth - 1, True, time_limit, start_time) 
            board.pop()

            if mate_in is None:
                return None, None
              
        best_mate_in = max(mate_in + 1 for move in board.legal_moves)

    return best_mate_in, best_move

def search_mate_for_move(move, board_fen, depth, time_limit, start_time):
    board = chess.Board(board_fen)
    board.push(move)
    mate_in, _ = search_mate(board, depth - 1, False, time_limit, start_time) 
    return mate_in, move

def detect_mate(fen, max_depth=20, time_limit=None):
    board = chess.Board(fen)
    start_time = time.time()

    for depth in range(1, max_depth + 1):
        legal_moves = list(board.legal_moves)

        # Parallelize across all legal moves
        with multiprocessing.Pool() as pool:
            results = pool.starmap(
                search_mate_for_move,
                [(move, board.fen(), depth, time_limit, start_time) for move in legal_moves]
            )

        # Process the results at the current depth
        best_mate_in = None
        best_move = None

        for mate_in, move in results:
            if mate_in is not None:
                if best_mate_in is None or mate_in < best_mate_in:
                    best_mate_in = mate_in
                    best_move = move

        if best_mate_in is not None:
            return best_mate_in, best_move

    # If no mate is found after searching all depths
    return None, None
