#!/usr/bin/env python3
"""
Step-by-step demonstration of search.py functions.
This shows how each function works with simple examples.
"""

from search import GameNode, is_terminal, expand_children, minimax
from board import Board
from heuristics import SimpleHeuristic
import numpy as np

def demo_step_by_step():
    """Demonstrate each function step by step"""
    print("STEP-BY-STEP DEMONSTRATION OF SEARCH.PY FUNCTIONS")
    print("=" * 60)
    
    # Setup
    game_n = 3  # 3 in a row to win
    heuristic = SimpleHeuristic(game_n)
    
    print("\n1. CREATING A GAME NODE")
    print("-" * 30)
    
    # Create a simple board
    board = Board(3, 3)
    print("Empty board:")
    print(board)
    
    # Create a game node
    node = GameNode(board, player_to_move=1, move=None, depth=0)
    print(f"GameNode created:")
    print(f"  - Player to move: {node.player_to_move}")
    print(f"  - Move: {node.move}")
    print(f"  - Depth: {node.depth}")
    
    print("\n2. TESTING is_terminal()")
    print("-" * 30)
    
    # Test empty board
    is_term = is_terminal(node, game_n)
    print(f"Empty board is terminal: {is_term}")
    
    # Test winning board
    win_board = Board(3, 3)
    win_board.play(0, 1)  # Player 1 plays column 0
    win_board.play(1, 1)  # Player 1 plays column 1  
    win_board.play(2, 1)  # Player 1 plays column 2 (wins!)
    
    print("\nWinning board:")
    print(win_board)
    
    win_node = GameNode(win_board, player_to_move=2)
    is_term = is_terminal(win_node, game_n)
    print(f"Winning board is terminal: {is_term}")
    
    print("\n3. TESTING expand_children()")
    print("-" * 30)
    
    # Start with empty board
    empty_board = Board(3, 3)
    empty_node = GameNode(empty_board, player_to_move=1)
    
    print("Expanding from empty board:")
    children = expand_children(empty_node)
    print(f"Number of children: {len(children)}")
    
    for i, child in enumerate(children):
        print(f"\nChild {i+1}:")
        print(f"  Move: column {child.move}")
        print(f"  Next player: {child.player_to_move}")
        print(f"  Depth: {child.depth}")
        print("  Board:")
        print(child.board)
    
    print("\n4. TESTING minimax()")
    print("-" * 30)
    
    # Test with a simple position
    test_board = Board(3, 3)
    test_board.play(0, 1)  # Player 1 plays column 0
    test_board.play(1, 1)  # Player 1 plays column 1
    
    print("Test board (Player 1 has two in a row):")
    print(test_board)
    
    test_node = GameNode(test_board, player_to_move=1)
    
    # Run minimax with depth 2
    depth = 2
    best_value = minimax(test_node, depth, game_n, 1, heuristic.evaluate_board)
    print(f"Best value for Player 1 (depth={depth}): {best_value}")
    
    # Show what each possible move leads to
    children = expand_children(test_node)
    print(f"\nAnalyzing each possible move:")
    for child in children:
        child_value = minimax(child, depth-1, game_n, 1, heuristic.evaluate_board)
        print(f"  Column {child.move}: value = {child_value}")
    
    print("\n5. COMPLETE MINIMAX PLAYER")
    print("-" * 30)
    
    def minimax_player_move(board, player_id, depth, game_n, heuristic):
        """Complete minimax player implementation"""
        root = GameNode(board, player_id)
        children = expand_children(root)
        
        if not children:
            return 0  # No valid moves
        
        best_move = 0
        best_value = -np.inf
        
        for child in children:
            child_value = minimax(child, depth-1, game_n, player_id, heuristic.evaluate_board)
            if child_value > best_value:
                best_value = child_value
                best_move = child.move
        
        return best_move
    
    # Test the complete player
    test_board2 = Board(3, 3)
    test_board2.play(0, 2)  # Player 2 plays column 0
    test_board2.play(1, 2)  # Player 2 plays column 1
    
    print("Test board (Player 2 has two in a row, Player 1's turn):")
    print(test_board2)
    
    best_move = minimax_player_move(test_board2, 1, 3, game_n, heuristic)
    print(f"Best move for Player 1: Column {best_move}")
    print("(Should be column 2 to block Player 2's win)")

if __name__ == "__main__":
    demo_step_by_step()
