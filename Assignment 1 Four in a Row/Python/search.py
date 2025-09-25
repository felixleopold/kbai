from __future__ import annotations
from typing import List, Optional, Tuple
from board import Board
import numpy as np

class GameNode:
    def __init__(self, board: Board, player_to_move: int, move: Optional[int] = None, depth: int = 0):
        self.board = board
        self.player_to_move = player_to_move
        self.move = move  # column used to reach this node from parent
        self.depth = depth
        self.children: List["GameNode"] = []
        self.value: Optional[int] = None  # heuristic/minimax value

def is_terminal(node: GameNode, game_n: int) -> bool:
    """
    Determines if the given node is a terminal state (win, loss, or draw).

    Args:
        node (GameNode): The game node to check.
        game_n (int): The number of discs in a row required to win.

    Returns:
        bool: True if the node is terminal, False otherwise.

    Pseudocode:
    Pseudocode:
    1. Get the current board state as a numpy array and store it in 'state'
    2. Use the app.winning function to check if the game is over:
       - Call app_winning(state, game_n) and store the result in 'result'
    3. If result is 1 (player 1 wins), 2 (player 2 wins), or -1 (draw):
       - Return True (the node is terminal)
    4. Otherwise:
       - Return False (the node is not terminal)
    """
    from app import winning as app_winning

    board_state = node.board.get_board_state()
    result = app_winning(board_state, game_n)
    # result = 1 or 2 if a player won, -1 if draw, 0 otherwise

    if result != 0:
        return True
    else:
        return False


def expand_children(node: GameNode) -> List["GameNode"]:
    """
    Expands a GameNode by generating all possible child nodes for the current player.

    Args:
        node (GameNode): The current game node to expand.

    Returns:
        List[GameNode]: A list of child GameNodes, one for each valid move.

    Pseudocode:

    Initialize an empty list called children
    For each column index from 0 to (width of the board - 1):
        If the move in this column is valid for the current board:
            - Create a new board by applying the move for the current player in this column
            - Determine the next player (if current player is 1, next is 2; if 2, next is 1)
            - Create a new GameNode with:
                - the new board
                - the next player to move
                - the column just played
                - depth increased by 1
            - Add this new GameNode to the children list
    Return the list of children GameNodes
    """
    children = []
    for col in range(node.board.width):
        if node.board.is_valid(col):
            new_board = node.board.get_new_board(col, node.player_to_move)
            childs_player_to_move = 3 - node.player_to_move # e.g. current player 1 -> 3 - 1 = 2 is next player
            child_node = GameNode(new_board, childs_player_to_move, col, node.depth + 1) # col is the col of the parent
            children.append(child_node)
    return children

def minimax(node: GameNode, depth: int, game_n: int, eval_player: int, evaluate_board) -> int:
    """
    Minimax algorithm implementation.
    
    Args:
        node: Current game node
        depth: Remaining search depth
        game_n: Number in a row to win
        eval_player: Player we're evaluating for (1 or 2)
        evaluate_board: Function to evaluate board positions
    
    Returns:
        Best value for the current node
    
    Pseudocode:
    If terminal OR depth == 0: return evaluate_board(eval_player, node.board) and node value
    Children generation: call expand_children(node)
    If node.player_to_move == eval_player: maximize, 
    start at -np.inf.
    Else: minimize, start at +np.inf.
    evaluate_board(eval_player, board)
    """
    
    return


### Core functions/methods you’ll use

# - Board.is_valid(col) -> bool
#   - Input: integer column index (0-based).
#   - Output: True if the top cell of that column is empty (a move can be played), else False.
#   - Use: filter legal moves during expansion.

# - Board.get_new_board(col, player_id) -> Board
#   - Input: column index (0-based), player id (1 or 2).
#   - Output: a new Board instance with the disc dropped into the lowest free cell of that column.
#   - Use: generate child nodes without mutating the parent board.

# - Board.get_board_state() -> np.ndarray
#   - Input: none.
#   - Output: a copy of the internal numpy array with shape (width, height).
#   - Use: pass to win detection and for any direct state inspection.

# - app.winning(state: np.ndarray, game_n: int) -> int
#   - Input: board state array (as above), target-in-a-row integer.
#   - Output: 1 or 2 if that player has won; -1 if draw; 0 otherwise.
#   - Use: terminal test to stop expanding or to return a terminal value.

# - Heuristic.evaluate_board(player_id: int, board: Board) -> int
#   - Input: the root (evaluation) player’s id, and a Board to evaluate.
#   - Output: integer utility. Terminal states get large ± values; otherwise max run length.
#   - Use: score leaf nodes (depth==0 or terminal).

# - Heuristic.get_best_action(player_id: int, board: Board) -> int
#   - Input: player id and Board.
#   - Output: column index (0-based) for the best one-ply move.
#   - Use: reference for sanity checks; it’s depth-1 only (not used inside minimax beyond debugging).

# - PlayerController fields available inside MinMax/AlphaBeta players
#   - self.player_id: 1 or 2 (whose turn for root).
#   - self.game_n: target in a row (e.g., 4).
#   - self.heuristic: attach to call evaluate_board or get_best_action.
#   - self.depth (in MinMax/AlphaBeta): maximum search depth (plies).


# =============================================================================
# TEST CASES - Run these to test each function individually
# =============================================================================

def create_test_board(state_array):
    """Helper function to create a board from a 2D array"""
    return Board(np.array(state_array).T)  # Transpose because Board expects (width, height)

def print_board_state(board, title="Board"):
    """Helper function to print board state nicely"""
    print(f"\n{title}:")
    print(board)
    print(f"Board state array:\n{board.get_board_state().T}")  # Transpose for display

def test_is_terminal():
    """Test the is_terminal function with different board situations"""
    print("=" * 60)
    print("TESTING is_terminal() FUNCTION")
    print("=" * 60)
    
    game_n = 3  # 3 in a row to win
    
    # Test Case 1: Empty board (not terminal)
    print("\n1. Empty board (should NOT be terminal):")
    empty_board = Board(3, 3)
    empty_node = GameNode(empty_board, 1)
    print_board_state(empty_board, "Empty Board")
    result = is_terminal(empty_node, game_n)
    print(f"Is terminal: {result}")
    
    # Test Case 2: Player 1 wins horizontally (terminal)
    print("\n2. Player 1 wins horizontally (should BE terminal):")
    win_board = create_test_board([
        [1, 1, 1],
        [0, 0, 0],
        [0, 0, 0]
    ])
    win_node = GameNode(win_board, 2)  # Player 2's turn but game is over
    print_board_state(win_board, "Player 1 Wins")
    result = is_terminal(win_node, game_n)
    print(f"Is terminal: {result}")
    
    # Test Case 3: Draw (board full, no winner)
    print("\n3. Draw situation (should BE terminal):")
    draw_board = create_test_board([
        [1, 2, 1],
        [2, 1, 2],
        [1, 2, 1]
    ])
    draw_node = GameNode(draw_board, 1)
    print_board_state(draw_board, "Draw Board")
    result = is_terminal(draw_node, game_n)
    print(f"Is terminal: {result}")
    
    # Test Case 4: Player 2 wins vertically (terminal)
    print("\n4. Player 2 wins vertically (should BE terminal):")
    win2_board = create_test_board([
        [2, 0, 0],
        [2, 0, 0],
        [2, 0, 0]
    ])
    win2_node = GameNode(win2_board, 1)
    print_board_state(win2_board, "Player 2 Wins")
    result = is_terminal(win2_node, game_n)
    print(f"Is terminal: {result}")

def test_expand_children():
    """Test the expand_children function and show the tree structure"""
    print("\n" + "=" * 60)
    print("TESTING expand_children() FUNCTION")
    print("=" * 60)
    
    # Test Case 1: Empty board
    print("\n1. Expanding from empty board (Player 1's turn):")
    empty_board = Board(3, 3)
    empty_node = GameNode(empty_board, 1)
    print_board_state(empty_board, "Root Board")
    
    children = expand_children(empty_node)
    print(f"\nNumber of children generated: {len(children)}")
    
    for i, child in enumerate(children):
        print(f"\nChild {i+1} (move to column {child.move}):")
        print_board_state(child.board, f"Child {i+1} Board")
        print(f"Next player to move: {child.player_to_move}")
        print(f"Depth: {child.depth}")
    
    # Test Case 2: Partially filled board
    print("\n" + "-" * 40)
    print("2. Expanding from partially filled board (Player 2's turn):")
    partial_board = create_test_board([
        [0, 0, 0],
        [1, 0, 0],
        [1, 2, 0]
    ])
    partial_node = GameNode(partial_board, 2)
    print_board_state(partial_board, "Root Board")
    
    children = expand_children(partial_node)
    print(f"\nNumber of children generated: {len(children)}")
    
    for i, child in enumerate(children):
        print(f"\nChild {i+1} (move to column {child.move}):")
        print_board_state(child.board, f"Child {i+1} Board")
        print(f"Next player to move: {child.player_to_move}")

def test_minimax():
    """Test the minimax function with different board positions"""
    print("\n" + "=" * 60)
    print("TESTING minimax() FUNCTION")
    print("=" * 60)
    
    from heuristics import SimpleHeuristic
    
    game_n = 3
    depth = 2
    heuristic = SimpleHeuristic(game_n)
    
    # Test Case 1: Empty board - find best move for Player 1
    print("\n1. Empty board - Player 1's turn (depth=2):")
    empty_board = Board(3, 3)
    empty_node = GameNode(empty_board, 1)
    print_board_state(empty_board, "Root Board")
    
    best_value = minimax(empty_node, depth, game_n, 1, heuristic.evaluate_board)
    print(f"Best value for Player 1: {best_value}")
    
    # Show children and their values
    children = expand_children(empty_node)
    print(f"\nChildren analysis:")
    for i, child in enumerate(children):
        child_value = minimax(child, depth-1, game_n, 1, heuristic.evaluate_board)
        print(f"  Column {child.move}: value = {child_value}")
    
    # Test Case 2: Near win situation for Player 1
    print("\n" + "-" * 40)
    print("2. Near win situation - Player 1 can win in 1 move:")
    near_win_board = create_test_board([
        [1, 1, 0],
        [0, 0, 0],
        [0, 0, 0]
    ])
    near_win_node = GameNode(near_win_board, 1)
    print_board_state(near_win_board, "Root Board")
    
    best_value = minimax(near_win_node, depth, game_n, 1, heuristic.evaluate_board)
    print(f"Best value for Player 1: {best_value}")
    
    # Test Case 3: Near loss situation - Player 2 can win
    print("\n" + "-" * 40)
    print("3. Near loss situation - Player 2 can win if Player 1 doesn't block:")
    near_loss_board = create_test_board([
        [2, 2, 0],
        [0, 0, 0],
        [0, 0, 0]
    ])
    near_loss_node = GameNode(near_loss_board, 1)
    print_board_state(near_loss_board, "Root Board")
    
    best_value = minimax(near_loss_node, depth, game_n, 1, heuristic.evaluate_board)
    print(f"Best value for Player 1: {best_value}")
    
    # Show children and their values
    children = expand_children(near_loss_node)
    print(f"\nChildren analysis:")
    for i, child in enumerate(children):
        child_value = minimax(child, depth-1, game_n, 1, heuristic.evaluate_board)
        print(f"  Column {child.move}: value = {child_value}")

def test_complete_minimax_player():
    """Test a complete minimax player implementation"""
    print("\n" + "=" * 60)
    print("TESTING COMPLETE MINIMAX PLAYER")
    print("=" * 60)
    
    from heuristics import SimpleHeuristic
    
    game_n = 3
    depth = 3
    heuristic = SimpleHeuristic(game_n)
    
    def minimax_player_move(board, player_id, depth, game_n, heuristic):
        """Complete minimax player implementation"""
        root = GameNode(board, player_id)
        
        # Get all possible moves
        children = expand_children(root)
        if not children:
            return 0  # No valid moves
        
        # Evaluate each move
        best_move = 0
        best_value = -np.inf
        
        for child in children:
            child_value = minimax(child, depth-1, game_n, player_id, heuristic.evaluate_board)
            if child_value > best_value:
                best_value = child_value
                best_move = child.move
        
        return best_move
    
    # Test Case 1: Empty board
    print("\n1. Empty board - Player 1's turn:")
    empty_board = Board(3, 3)
    print_board_state(empty_board, "Initial Board")
    
    best_move = minimax_player_move(empty_board, 1, depth, game_n, heuristic)
    print(f"Best move for Player 1: Column {best_move}")
    
    # Test Case 2: Near win situation
    print("\n2. Near win situation - Player 1's turn:")
    near_win_board = create_test_board([
        [1, 1, 0],
        [0, 0, 0],
        [0, 0, 0]
    ])
    print_board_state(near_win_board, "Initial Board")
    
    best_move = minimax_player_move(near_win_board, 1, depth, game_n, heuristic)
    print(f"Best move for Player 1: Column {best_move}")
    
    # Test Case 3: Defensive situation
    print("\n3. Defensive situation - Player 1 must block Player 2:")
    defensive_board = create_test_board([
        [2, 2, 0],
        [0, 0, 0],
        [0, 0, 0]
    ])
    print_board_state(defensive_board, "Initial Board")
    
    best_move = minimax_player_move(defensive_board, 1, depth, game_n, heuristic)
    print(f"Best move for Player 1: Column {best_move}")

def run_all_tests():
    """Run all test functions"""
    print("STARTING COMPREHENSIVE TESTS FOR SEARCH.PY FUNCTIONS")
    print("Using 3x3 board with 3-in-a-row winning condition")
    
    test_is_terminal()
    test_expand_children()
    test_minimax()
    test_complete_minimax_player()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED!")
    print("=" * 60)

# Individual test functions you can call separately
def test_individual_functions():
    """Run individual test functions one by one"""
    print("Available individual tests:")
    print("1. test_is_terminal() - Test terminal state detection")
    print("2. test_expand_children() - Test tree expansion")
    print("3. test_minimax() - Test minimax algorithm")
    print("4. test_complete_minimax_player() - Test complete player")
    print("5. run_all_tests() - Run all tests")
    print("\nExample usage:")
    print("  test_is_terminal()")
    print("  test_expand_children()")
    print("  test_minimax()")

if __name__ == "__main__":
    # Uncomment the test you want to run:
    
    # Run all tests
    run_all_tests()
    
    # Or run individual tests:
    # test_is_terminal()
    # test_expand_children() 
    # test_minimax()
    # test_complete_minimax_player()