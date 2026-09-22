def is_valid_move(board, src, dest):
    """
    Validate a move on the board. Returns True if the move is valid, else False.
    """

    # Extract board dimensions
    rows, cols = len(board), len(board[0]) if board else (0, 0)

    # Check if src and dest are within the board's bounds
    if (not 0 <= src[0] < rows) or (not 0 <= src[1] < cols):
        return False
    if not (0 <= dest[0] < rows and 0 <= dest[1] < cols):
        return False

    # Retrieve the pieces at the source and destination
    src_piece = board[src[0]][src[1]]
    dest_piece = board[dest[0]][dest[1]]

    # Check if the source contains a player's piece and destination is not the same or belongs to the opposite player
    if src_piece in ('X', 'O') and dest_piece in ('X', 'O') and src_piece != dest_piece:
        return True

    return False

# Test cases
board1 = [
    [None, 'X', None],
    [None, 'O', None],
    [None, None, None]
]

print(is_valid_move(board1, (0, 1), (2, 1)))  # True, 'X' moves to an empty square
print(is_valid_move(board1, (0, 0), (0, 2)))  # True, 'X' moves to an empty square
print(is_valid_move(board1, (1, 1), (2, 1)))  # False, 'O' is already at the destination
print(is_valid_move(board1, (2, 0), (1, 0)))  # False, 'None' cannot be a valid move
print(is_valid_move(board1, (0, 1), (0, 1)))  # False, the same place
