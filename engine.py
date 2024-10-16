import chess
import tactics
import checkmate
import time
import openings

EARLY_GAME_MOVE_LIMIT = 10  # Define early game as the first 10 moves

PAWN_TABLE = [
    100, 100, 100, 100, 100, 100, 100, 100,
    5, 5, 5, -10, -10, 5, 5, 5,
    5, -5, -5, 0, 0, -5, -5, 5,
    0, 0, 0, 20, 20, -10, -10, -10,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    100, 100, 100, 100, 100, 100, 100, 100
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, -5, 0, 0, -5, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

ROOK_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0
]

QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

KING_TABLE_MIDDLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20
]

KING_TABLE_ENDGAME = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]

def get_positional_value(piece, square, is_white, is_endgame):
    """
    Returns the positional value for a piece on a specific square.
    """
    if piece == chess.PAWN:
        table = PAWN_TABLE
    elif piece == chess.KNIGHT:
        table = KNIGHT_TABLE
    elif piece == chess.BISHOP:
        table = BISHOP_TABLE
    elif piece == chess.ROOK:
        table = ROOK_TABLE
    elif piece == chess.QUEEN:
        table = QUEEN_TABLE
    elif piece == chess.KING:
        # Use different tables based on the game phase
        table = KING_TABLE_ENDGAME if is_endgame else KING_TABLE_MIDDLE
    else:
        return 0  # No positional value for invalid pieces

    # Use mirrored table for black pieces
    if is_white:
        return table[square]
    else:
        return table[chess.square_mirror(square)]

def is_open_file(board, square):
    """
    Returns True if the file of the given square is open (i.e., no pawns on that file).
    """
    file = chess.square_file(square)
    for rank in range(8):
        piece = board.piece_at(chess.square(file, rank))
        if piece and piece.piece_type == chess.PAWN:
            return False
    return True

def evaluate_rook_activity(board):
    """
    Evaluates rook activity for both players, giving a bonus for control of open or semi-open files.
    """
    rook_activity_value = 0
    for color, factor in [(chess.WHITE, 1), (chess.BLACK, -1)]:
        for square in board.pieces(chess.ROOK, color):
            if is_open_file(board, square):
                rook_activity_value += factor * 40
            elif is_semi_open_file(board, square, color):
                rook_activity_value += factor * 20
    return rook_activity_value

def is_semi_open_file(board, square, color):
    """
    Returns True if the file of the given square is semi-open (i.e., only opponent's pawns are on the file).
    """
    file = chess.square_file(square)
    for rank in range(8):
        piece = board.piece_at(chess.square(file, rank))
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            return False
    return True

def is_piece_defended(board, square, color):
    defenders = board.attackers(color, square)
    return len(defenders) > 0

def is_endgame(board):
    """
    A heuristic to determine if the game is in the endgame.
    """
    queens = board.pieces(chess.QUEEN, chess.WHITE) | board.pieces(chess.QUEEN, chess.BLACK)
    minor_pieces = (board.pieces(chess.KNIGHT, chess.WHITE) | board.pieces(chess.BISHOP, chess.WHITE) |
                    board.pieces(chess.KNIGHT, chess.BLACK) | board.pieces(chess.BISHOP, chess.BLACK))
    return not queens or len(minor_pieces) <= 2

def is_mate_in_one(board, color):
    """
    Checks if the given player can deliver checkmate in one move.
    """
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return True
        board.pop()
    return False

def check_development_penalty(board, move_number, expected_development_by_move=10):
    """
    Penalizes the bot if not all pieces that should be developed have moved by a certain move number.
    
    Arguments:
    board: chess.Board() object representing the current board state.
    move_number: The current move number.
    expected_development_by_move: Move number by which pieces are expected to be developed. Default is 10.

    Returns:
    int: The total penalty points deducted for undeveloped pieces.
    """

    penalty = 0
    undeveloped_pieces = []

    # Define starting positions for knights, bishops, queen, and rooks
    undeveloped_positions_white = {
        "knights": [chess.B1, chess.G1],
        "bishops": [chess.C1, chess.F1],
        "queen": [chess.D1],
        "rooks": [chess.A1, chess.H1]  # Rooks usually developed later
    }
    undeveloped_positions_black = {
        "knights": [chess.B8, chess.G8],
        "bishops": [chess.C8, chess.F8],
        "queen": [chess.D8],
        "rooks": [chess.A8, chess.H8]
    }

    # Check for undeveloped pieces on the board
    if board.turn == chess.WHITE:
        # For white's turn
        for piece_type, positions in undeveloped_positions_white.items():
            for pos in positions:
                if board.piece_at(pos) is not None and board.piece_at(pos).color == chess.WHITE:
                    undeveloped_pieces.append(piece_type)
                    penalty += 1  # Add penalty for each undeveloped piece

    else:
        # For black's turn
        for piece_type, positions in undeveloped_positions_black.items():
            for pos in positions:
                if board.piece_at(pos) is not None and board.piece_at(pos).color == chess.BLACK:
                    undeveloped_pieces.append(piece_type)
                    penalty += 1  # Add penalty for each undeveloped piece

    # Apply penalty only if the move number is beyond the expected development stage
    if move_number > expected_development_by_move:
        return penalty
    else:
        return 0  # No penalty before the expected development move number

def is_passed_pawn(board, square, color):
    """
    Determines if a pawn is a passed pawn.
    A passed pawn has no opposing pawns in front of it on the same or adjacent files.
    """
    file = chess.square_file(square)
    direction = 1 if color == chess.WHITE else -1
    for f in range(max(0, file - 1), min(7, file + 1) + 1):
        for r in range(chess.square_rank(square) + direction, 8 if color == chess.WHITE else -1, direction):
            test_square = chess.square(f, r)
            if board.piece_at(test_square) and board.piece_at(test_square).piece_type == chess.PAWN and board.piece_at(test_square).color != color:
                return False
    return True

def has_doubled_pawn(pawns, file):
    """
    Determines if there are two pawns of the same color on the same file.
    """
    return sum(1 for square in pawns if chess.square_file(square) == file) > 1

def is_isolated_pawn(board, square, color):
    """
    Determines if a pawn is isolated.
    """
    file = chess.square_file(square)
    pawns = board.pieces(chess.PAWN, color)
    for adj_file in [file - 1, file + 1]:
        if 0 <= adj_file <= 7 and any(chess.square_file(pawn) == adj_file for pawn in pawns):
            return False
    return True

def is_backward_pawn(board, square, color):
    """
    Determines if a pawn is backward.
    """
    file = chess.square_file(square)
    direction = 1 if color == chess.WHITE else -1
    pawns = board.pieces(chess.PAWN, color)
    for adj_file in [file - 1, file + 1]:
        if 0 <= adj_file <= 7:
            for adj_rank in range(chess.square_rank(square) + direction, 8 if color == chess.WHITE else -1, direction):
                if chess.square(adj_file, adj_rank) in pawns:
                    return False
    for r in range(chess.square_rank(square) + direction, 8 if color == chess.WHITE else -1, direction):
        test_square = chess.square(file, r)
        if board.piece_at(test_square) and board.piece_at(test_square).piece_type == chess.PAWN and board.piece_at(test_square).color != color:
            return True
    return False



def evaluate_pawn_advancement(board, color):
    """
    Encourages pawn advancement toward promotion.
    Stronger encouragement for passed pawns in the endgame.
    """
    advancement_score = 0
    direction = 1 if color == chess.WHITE else -1
    rank_goal = 7 if color == chess.WHITE else 0
    is_endgame_phase = is_endgame(board)

    for square in board.pieces(chess.PAWN, color):
        rank = chess.square_rank(square)
        advancement_score += (7 - abs(rank_goal - rank)) * 10  # Encourage advancement

        # Additional bonus for passed pawns
        if is_passed_pawn(board, square, color):
            advancement_score += 30 if is_endgame_phase else 20  # Stronger bonus in the endgame

        # Bonus for pawns reaching the 7th rank (or 2nd for black) since they are close to promotion
        if rank == (6 if color == chess.WHITE else 1):
            advancement_score += 40

    return advancement_score


def evaluate_pawn_structure(board, is_endgame):
    """
    Evaluates pawn structure, considering passed, doubled, isolated, and backward pawns.
    """
    pawn_structure_score = 0
    bonuses = {"passed": (30 if is_endgame else 15), "doubled": -20, "isolated": -25, "backward": -15}
    for color, factor in [(chess.WHITE, 1), (chess.BLACK, -1)]:
        pawns = board.pieces(chess.PAWN, color)
        for square in pawns:
            file = chess.square_file(square)
            if is_passed_pawn(board, square, color):
                pawn_structure_score += factor * bonuses["passed"]
            if has_doubled_pawn(pawns, file):
                pawn_structure_score += factor * bonuses["doubled"]
            if is_isolated_pawn(board, square, color):
                pawn_structure_score += factor * bonuses["isolated"]
            if is_backward_pawn(board, square, color):
                pawn_structure_score += factor * bonuses["backward"]
    return pawn_structure_score * 0.5

def evaluate_queen_trade(board, material_advantage):
    """
    Evaluates whether a queen trade is favorable based on material advantage.
    """
    white_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
    if white_queens > 0 and black_queens > 0:
        if material_advantage > 0:
            return 50
        elif material_advantage < 0:
            return -50
    return 0

def is_early_game(board):
    """
    Determines if the game is in the early phase based on the move count.
    """
    return board.fullmove_number <= EARLY_GAME_MOVE_LIMIT

def penalize_early_queen_use(board):
    """
    Apply a strong penalty if the queen is moved early in the game before minor pieces are developed.
    """
    penalty = 0
    if is_early_game(board):
        for color, factor in [(chess.WHITE, -1000), (chess.BLACK, 1000)]:
            queens = board.pieces(chess.QUEEN, color)
            # Minor pieces developed
            minor_pieces_developed = (len(board.pieces(chess.KNIGHT, color)) + len(board.pieces(chess.BISHOP, color))) >= 4
            
            for queen_square in queens:
                # Penalize if queen is moved before full development of knights and bishops
                if not minor_pieces_developed:
                    penalty += factor * 2  # Double penalty for early queen use
    return penalty

def penalize_multiple_piece_moves(board):
    """
    Apply a penalty for moving the same piece multiple times in the early game.
    """
    penalty = 0
    if is_early_game(board):
        piece_move_count = {}

        # Count moves for each piece
        for move in board.move_stack:
            piece_type = board.piece_type_at(move.from_square)
            piece_color = board.color_at(move.from_square)

            piece_id = (piece_color, piece_type)
            if piece_id not in piece_move_count:
                piece_move_count[piece_id] = 0
            piece_move_count[piece_id] += 1

        # Penalize if any piece has been moved more than once
        for count in piece_move_count.values():
            if count > 1:
                penalty += (count - 1) * 50  # Adjust penalty weight as necessary

    return penalty

def evaluate_king_safety(board, color):
    """
    Evaluate king safety for the given color.
    King safety is affected by pawn structure around the king and enemy pieces near the king.
    Penalizes for open files near the king, lack of castling, and exposed positions.
    """
    king_square = board.king(color)
    safety_score = 0
    file = chess.square_file(king_square)
    rank = chess.square_rank(king_square)
    direction = 1 if color == chess.WHITE else -1

    # Check the three squares in front of the king (same file, adjacent files)
    for adj_file in [file - 1, file, file + 1]:
        if 0 <= adj_file <= 7:  # Ensure the file is valid
            pawn_square = chess.square(adj_file, rank + direction)
            piece = board.piece_at(pawn_square)
            if piece is None or piece.piece_type != chess.PAWN or piece.color != color:
                safety_score -= 20  # Penalize lack of pawn protection

    # Penalize the king for being exposed on an open file
    if is_open_file(board, king_square):
        safety_score -= 30

    # Penalize the king for being close to enemy pieces
    enemy_pieces = board.attackers(not color, king_square)
    safety_score -= len(enemy_pieces) * 10  # Penalize proximity of enemy pieces

    # Penalize if the king hasn't castled yet
    if not board.has_castling_rights(color):
        safety_score -= 50  # Heavier penalty for not castling

    return safety_score


def evaluate_board(board):
    """
    Static evaluation of the board using bitboards. Positive values favor White, negative values favor Black.
    This function includes material, positional, and pawn structure evaluations.
    Additionally, it checks for mate-in-one, rook activity, and penalizes repeated positions and early queen moves.
    """
    piece_values = {
        chess.PAWN: 500,
        chess.KNIGHT: 3050,
        chess.BISHOP: 3330,
        chess.ROOK: 5630,
        chess.QUEEN: 9500,
        chess.KING: 0  # King has no value, game ends if checkmated
    }

    value = 0
    is_endgame_phase = is_endgame(board)

    # Evaluate each piece type for both players
    for piece_type in piece_values:
        # Get bitboards for each piece type
        white_pieces = board.pieces(piece_type, chess.WHITE)
        black_pieces = board.pieces(piece_type, chess.BLACK)

        # Material value for each piece
        value += len(white_pieces) * piece_values[piece_type]
        value -= len(black_pieces) * piece_values[piece_type]

        # Positional value based on the positional tables
        for square in white_pieces:
            value += get_positional_value(piece_type, square, is_white=True, is_endgame=is_endgame_phase)

        for square in black_pieces:
            value -= get_positional_value(piece_type, square, is_white=False, is_endgame=is_endgame_phase)

    # Pawn structure evaluation
    value += evaluate_pawn_structure(board, is_endgame_phase)
    if chess.WHITE:
        value += tactics.evaluate_tactics(board)
    if chess.BLACK:
        value += tactics.evaluate_tactics(board)
    value += evaluate_rook_activity(board)

    # Penalize repeated positions (discourages shuffling)
    if board.is_repetition():
        value -= 50 if board.turn == chess.BLACK else 50  # Penalty for repetition

    # Penalize early queen moves
    if chess.WHITE:
        value -= penalize_early_queen_use(board)
    if chess.BLACK:
        value -= penalize_early_queen_use(board)
    value += evaluate_king_safety(board, chess.WHITE)
    value -= evaluate_king_safety(board, chess.BLACK)
    value -= check_development_penalty(board, chess.BLACK)
    value -= check_development_penalty(board, chess.WHITE)
    for square in black_pieces:
        value -= is_piece_defended(board, square, chess.BLACK)
        value += is_piece_defended(board, square, chess.BLACK)
    if chess.WHITE:
        value += penalize_multiple_piece_moves(board)
    if chess.BLACK:
        value -= penalize_multiple_piece_moves(board)

    if is_endgame_phase:
        value += evaluate_pawn_advancement(board, chess.WHITE)
        value -= evaluate_pawn_advancement(board, chess.BLACK)

    return value


# Function to check if the current position is a checkmate
def is_checkmate(board):
    return board.is_checkmate()

def find_best_move_with_mate_in_one_prevention(board):
    """
    Finds the best move while ensuring that the move does not lead to a mate-in-one situation for the opponent.
    """
    best_move = None
    best_value = -float('inf') if board.turn == chess.WHITE else float('inf')

    # Iterate over all legal moves
    for move in board.legal_moves:
        board.push(move)

        # Check if the opponent has a mate-in-one after this move
        if not is_mate_in_one(board, not board.turn):  # Opponent's turn after the move
            # Evaluate the resulting board position
            eval_value = evaluate_board(board)

            # For white, maximize value. For black, minimize value.
            if board.turn == chess.WHITE and eval_value > best_value:
                best_value = eval_value
                best_move = move
            elif board.turn == chess.BLACK and eval_value < best_value:
                best_value = eval_value
                best_move = move

        board.pop()  # Undo the move

    return best_move

def detect_mate_in_one(board):
    """
    Check if there's a mate in one move and return the move if found.
    """
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move  # Return the move that causes checkmate
        board.pop()
    return None

def minimax(board, depth, alpha, beta, maximizing_player, last_move=None):
    """
    Minimax algorithm with alpha-beta pruning using bitboards.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None

    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)

            # Detect and penalize shuffling (moving a piece back and forth between two squares)
            if last_move and move.from_square == last_move.to_square and move.to_square == last_move.from_square:
                eval = -1000  # Heavy penalty for shuffling
            else:
                eval, _ = minimax(board, depth - 1, alpha, beta, False, last_move=move)

            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move

            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)

            # Detect and penalize shuffling (moving a piece back and forth between two squares)
            if last_move and move.from_square == last_move.to_square and move.to_square == last_move.from_square:
                eval = 1000  # Heavy penalty for shuffling
            else:
                eval, _ = minimax(board, depth - 1, alpha, beta, True, last_move=move)

            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move

            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def run_chess_bot(board, depth=4):
    move_history = list(board.move_stack)

    # Use opening book if the current move sequence matches any sequence in the book
    opening_move = openings.find_move_in_book(board)

    if opening_move:
        print(opening_move)
        opening_move = chess.Move.from_uci(opening_move)
        # Convert the UCI string move from the opening book to a chess.Move object
        return opening_move

	
    # Check for mate in one
    mate = detect_mate_in_one(board)
    if mate is not None:
        return mate

    bfen = board.fen()
    time_limit = 5
    mate_in, best_move = checkmate.detect_mate(bfen, max_depth=5, time_limit=time_limit)
    if mate_in is not None:
        print("mate found")
        return best_move

    bot_color = chess.WHITE if board.turn == chess.WHITE else chess.BLACK
        # Check for mate
    time_limit = 5.0
    mate_three = detect_mate_in_three(board, bot_color, time_limit)
    print(mate_three)
    if mate_three:
        print("Mate in n!")
        return mate_three

    # Count the number of legal moves directly
    legal_moves_count = len(list(board.legal_moves))

    # Set depth based on the number of legal moves
    if legal_moves_count == 1:
        depth = 1
    elif legal_moves_count < 11:
        depth = 4
    else:
        depth = 3

    # Proceed with minimax for the best move
    print("minimax")
    _, best_move = minimax(board, depth, -float('inf'), float('inf'), board.turn == chess.WHITE)
    return best_move
