import random
import chess

def find_move_in_book(board, book_file="Book.txt"):
    fen_input = board.fen().strip()  # Ensure FEN is stripped of any surrounding whitespace
    fen_input = fen_input.replace(" 0 1", "") # Replace "0 1" with an empty string to remove it
    print(fen_input)
    try:
        with open(book_file, 'r') as file:
            lines = file.readlines()

        fen_found = False
        moves = []

        for line in lines:
            line = line.strip()

            if line.startswith('pos'):  # Line defines a new FEN position
                current_fen = line.split('pos ', 1)[1].strip()  # Handle splitting safely
                if current_fen == fen_input:
                    fen_found = True
                    moves = []  # Reset moves for the matching position
                else:
                    fen_found = False  # No match, continue looking

            elif fen_found:  # Collect moves if we found the correct FEN
                if not line:  # Break if the line is empty
                    break
                move_data = line.split()
                if move_data:
                    moves.append(move_data[0])  # Add move (first element) only if it's valid

        if moves:
            move = random.choice(moves)  # Randomly select a move from the available ones
            print(move)
            return move
        else:
            print("None")
            return None  # No moves found for the position

    except FileNotFoundError:
        print(f"The file '{book_file}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
