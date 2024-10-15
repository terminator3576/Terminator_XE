import chess
import threading

# Define piece values
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

def detect_forks(board, attacks_cache, result, index):
    fork_score = 0
    # Check knights, queens, and now pawns for possible forks
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.piece_type not in {chess.KNIGHT, chess.QUEEN, chess.PAWN}:
            continue

        if piece.piece_type == chess.PAWN:
            pawn_attack_squares = board.attacks(square) 
            targets = [target for target in pawn_attack_squares
                       if board.piece_at(target) and piece_values[board.piece_at(target).piece_type] > piece_values[chess.PAWN]]
        else:
            attackers = attacks_cache.get(square, set())
            targets = [target for target in board.attacks(square)
                       if board.piece_at(target) and piece_values[board.piece_at(target).piece_type] > piece_values[piece.piece_type]]
          
        if len(targets) >= 2:
            fork_score += sum(piece_values[board.piece_at(target).piece_type] for target in targets)

    result[index] = fork_score


def detect_skewers(board, attacks_cache, result, index):
    skewer_score = 0
    # Long-range pieces: bishops, rooks, queens
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.piece_type not in {chess.BISHOP, chess.ROOK, chess.QUEEN}:
            continue
        
        for target_square in board.attacks(square):
            # Check for skewer conditions
            if board.piece_at(target_square) and board.is_pinned(not board.turn, target_square):
                skewer_score += piece_values[board.piece_at(target_square).piece_type]

    result[index] = skewer_score

def detect_pins(board, attacks_cache, result, index):
    pin_score = 0
    # Long-range pieces: bishops, rooks, queens
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.piece_type not in {chess.BISHOP, chess.ROOK, chess.QUEEN}:
            continue

        for target_square in board.attacks(square):
            if board.is_pinned(not board.turn, target_square):
                pinned_piece = board.piece_at(target_square)
                if pinned_piece:
                    pin_score += piece_values[pinned_piece.piece_type]

    result[index] = pin_score

def detect_discovered_attacks(board, attacks_cache, result, index):
    discovered_attack_score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type in {chess.BISHOP, chess.ROOK, chess.QUEEN}:
            for target_square in board.attacks(square):
                if board.is_pinned(not board.turn, square) and board.piece_at(target_square):
                    discovered_attack_score += piece_values[board.piece_at(target_square).piece_type]

    result[index] = discovered_attack_score

def evaluate_tactics(board):
    if board.is_game_over() or board.fullmove_number < 5:
        return 0  # Skip tactics if the game is over or in very early moves.

    # Precompute attacks for all pieces
    attacks_cache = {square: board.attacks(square) for square in chess.SQUARES}

    # Only evaluate tactics when there are queens or rooks on the board
    if not (board.pieces(chess.QUEEN, chess.WHITE) or board.pieces(chess.QUEEN, chess.BLACK) or 
            board.pieces(chess.ROOK, chess.WHITE) or board.pieces(chess.ROOK, chess.BLACK)):
        return 0  # Skip tactics when there are no major attacking pieces left

    result = [0] * 4 

    # Start threads for each tactic
    threads = []
    threads.append(threading.Thread(target=detect_forks, args=(board, attacks_cache, result, 0)))
    threads.append(threading.Thread(target=detect_skewers, args=(board, attacks_cache, result, 1)))
    threads.append(threading.Thread(target=detect_pins, args=(board, attacks_cache, result, 2)))
    threads.append(threading.Thread(target=detect_discovered_attacks, args=(board, attacks_cache, result, 3)))

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
      
    total_score = sum(result)

    return total_score * 2
