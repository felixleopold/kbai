from __future__ import annotations
from abc import abstractmethod
import numpy as np
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from heuristics import Heuristic
    from board import Board

# Control randomness in AI moves - when True, always choose the first best move
FIX_RANDOMNESS = True

class PlayerController:
    """Abstract class defining a player
    """
    def __init__(self, player_id: int, game_n: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            heuristic (Heuristic): heuristic used by the player
        """
        self.player_id = player_id
        self.game_n = game_n
        self.heuristic = heuristic


    def get_eval_count(self) -> int:
        """
        Returns:
            int: The amount of times the heuristic was used to evaluate a board state
        """
        return self.heuristic.eval_count
    

    def __str__(self) -> str:
        """
        Returns:
            str: representation for representing the player on the board
        """
        if self.player_id == 1:
            return 'X'
        return 'O'
        

    @abstractmethod
    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        pass


class MinMaxPlayer(PlayerController):
    """Class for the minmax player using the minmax algorithm
    Inherits from Playercontroller
    """
    def __init__(self, player_id: int, game_n: int, depth: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            depth (int): the max search depth
            heuristic (Heuristic): heuristic used by the player
        """
        super().__init__(player_id, game_n, heuristic)
        self.depth: int = depth


    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """

        # TODO: implement minmax algortihm!
        # INT: use the functions on the 'board' object to produce a new board given a specific move
        # HINT: use the functions on the 'heuristic' object to produce evaluations for the different board states!

        best_value: float = -np.inf # negative infinity
        best_cols: list[int] = [] # add best moves to a list and choose randomly to avoid left-bias
        for col in range(board.width):
            if board.is_valid(col):
                new_board: Board = board.get_new_board(col, self.player_id)
                new_board_eval: int = self.minmax(new_board, self.depth, False) # not depth -1 to avoid off-by-one error
                if new_board_eval > best_value:
                    best_value = new_board_eval
                    best_cols = [col]
                elif new_board_eval == best_value:
                    best_cols.append(col)

        # This returns the same as
        self.heuristic.get_best_action(self.player_id, board) # Very useful helper function!

        # Your assignment is to create a data structure (tree) to store the gameboards such that you can evaluate a higher depths.
        # Then, use the minmax algorithm to search through this tree to find the best move/action to take!

        # Select among moves with the best evaluation - either randomly or deterministically
        return best_cols[0] if FIX_RANDOMNESS else random.choice(best_cols)
    
    
    # =============================== Helper function ===============================
    #           Helper function to check if the node is a terminal state
    # ===============================================================================

    def _is_terminal(self, board: Board) -> bool:
        """
        Determines if the given node is a terminal state (win, loss, or draw).

        Args:
            board (Board): The current board.

        Returns:
            bool: True if the node is terminal, False otherwise.

        Pseudocode:
            1. Get the current board state as a numpy array and store it in 'state'
            2. Use the winning function to check if the game is over:
                - Call winning(state, game_n) and store the result in 'result'
            3. If result is 1 (player 1 wins), 2 (player 2 wins), or -1 (draw):
                - Return True (the node is terminal)
            4. Otherwise:
                - Return False (the node is not terminal)
        """
        state = board.get_board_state()
        result = self.heuristic.winning(state, self.game_n)
        # result = 1 or 2 if a player won, -1 if draw, 0 otherwise

        if result != 0:
            return True
        else:
            return False


    # =============================== Minmax algorithm ===============================  
    #       Minmax algorithm to find the best move for the current player.
    # ================================================================================

    def minmax(self, board: Board, depth: int, is_maximising: bool) -> int:
        """
        Args:
            board (Board): The current board.
            depth (int): The current depth of the search.
            is_maximising (bool): Whether the current player is maximizing or minimizing.

        Returns:
            int: The best evaluation for the current player.
        """
        # Base case: depth limit reached or terminal state
        # -------------------------------------------------
        if depth == 0 or self._is_terminal(board):
            return self.heuristic.evaluate_board(self.player_id, board) # How good is this board for me (player_id)?



        # Recursive case 1:
        # -------------------------------------------------

        # If we are evaluatin the score form our own perspective
        if is_maximising:

            # Initialize the best evaluation so far with minus infinity
            best_eval = -np.inf

            # Go through all the columns
            for col in range(board.width):
                # If we can still place a piece in this column
                if board.is_valid(col):
                    # Create a new board (child node) with the hypothetical move for this column for ourself
                    child: Board = board.get_new_board(col, self.player_id)
                    
                    # Get the value for the child by calling the function recursively with depth -1 and is_maximising False
                    child_eval: int = self.minmax(child, depth -1, False)

                    # If the child evaluation is better than the best evaluation so far, update the best evaluation
                    if child_eval > best_eval:
                        best_eval = child_eval

            # After going through all the columns, return the best evaluation
            return best_eval



        # Recursive case 2:
        # -------------------------------------------------

        # If we are evaluation the score based on how the opponent would act
        else: 

            # Initialize the worst evaluation so far with infinity
            worst_eval = np.inf

            # Get Opponent ID by swapping assigning 1 if current player is 2 else 2
            opp: int = 1 if self.player_id == 2 else 2

            # Go through all the columns
            for col in range(board.width):
                # If we can still place a piece in this column
                if board.is_valid(col):
                    # Create a new board (child node) with the hypothetical move for this column for the opponent
                    child: Board = board.get_new_board(col, opp)
                    
                    # Get the value for the child by calling the function recursively with depth -1 and is_maximising False
                    child_eval: int = self.minmax(child, depth -1, True)

                    # If the child evaluation is better than the best evaluation so far, update the best evaluation
                    if child_eval < worst_eval:
                        worst_eval = child_eval

            # After going through all the columns, return the worst evaluation (which is the best for the player)
            return worst_eval

    

class AlphaBetaPlayer(PlayerController):
    """Class for the minmax player using the minmax algorithm with alpha-beta pruning
    Inherits from Playercontroller
    """
    def __init__(self, player_id: int, game_n: int, depth: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            depth (int): the max search depth
            heuristic (Heuristic): heuristic used by the player
        """
        super().__init__(player_id, game_n, heuristic)
        self.depth: int = depth


    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """

        # TODO: implement minmax algorithm with alpha beta pruning!

        best_value: float = -np.inf # negative infinity
        best_cols: list[int] = []
        for col in range(board.width):
            if board.is_valid(col):
                new_board: Board = board.get_new_board(col, self.player_id)
                new_board_eval: int = self.alphabeta(new_board, self.depth, False, -np.inf, np.inf)
                if new_board_eval > best_value:
                    best_value = new_board_eval
                    best_cols = [col]
                elif new_board_eval == best_value:
                    best_cols.append(col)

        # This returns the same as
        self.heuristic.get_best_action(self.player_id, board) # Very useful helper function!

        # Your assignment is to create a data structure (tree) to store the gameboards such that you can evaluate a higher depths.
        # Then, use the minmax algorithm to search through this tree to find the best move/action to take!

        # Select among moves with the best evaluation - either randomly or deterministically
        return best_cols[0] if FIX_RANDOMNESS else random.choice(best_cols)
    
    
    # =============================== Helper function ===============================
    #           Helper function to check if the node is a terminal state
    # ===============================================================================

    def _is_terminal(self, board: Board) -> bool:
        """
        Determines if the given node is a terminal state (win, loss, or draw).

        Args:
            board (Board): The current board.

        Returns:
            bool: True if the node is terminal, False otherwise.

        Pseudocode:
            1. Get the current board state as a numpy array and store it in 'state'
            2. Use the winning function to check if the game is over:
                - Call winning(state, game_n) and store the result in 'result'
            3. If result is 1 (player 1 wins), 2 (player 2 wins), or -1 (draw):
                - Return True (the node is terminal)
            4. Otherwise:
                - Return False (the node is not terminal)
        """
        state = board.get_board_state()
        result = self.heuristic.winning(state, self.game_n)
        # result = 1 or 2 if a player won, -1 if draw, 0 otherwise

        if result != 0:
            return True
        else:
            return False


    # =============================== AlphaBeta algorithm ===============================  
    #       AlphaBeta algorithm to find the best move for the current player.
    # ================================================================================

    def alphabeta(self, board: Board, depth: int, is_maximising: bool, alpha: int, beta: int) -> int:
        """
        Args:
            board (Board): The current board.
            depth (int): The current depth of the search.
            is_maximising (bool): Whether the current player is maximizing or minimizing.
            alpha (int): The alpha value for the current player.
            beta (int): The beta value for the current player.

        Returns:
            int: The best evaluation for the current player.
        """
        # Base case: depth limit reached or terminal state
        # -------------------------------------------------
        if depth == 0 or self._is_terminal(board):
            return self.heuristic.evaluate_board(self.player_id, board) # How good is this board for me (player_id)?



        # Recursive case 1:
        # -------------------------------------------------

        # If we are evaluatin the score form our own perspective
        if is_maximising:

            # Initialize the best evaluation so far with minus infinity
            best_eval = -np.inf

            # Go through all the columns
            for col in range(board.width):
                # If we can still place a piece in this column
                if board.is_valid(col):
                    # Create a new board (child node) with the hypothetical move for this column for ourself
                    child: Board = board.get_new_board(col, self.player_id)
                    
                    # Get the value for the child by calling the function recursively with depth -1 and is_maximising False
                    child_eval: int = self.alphabeta(child, depth -1, False, alpha, beta)

                    # If the child evaluation is better than the best evaluation so far, update the best evaluation
                    if child_eval > best_eval:
                        best_eval = child_eval

                    # Update the alpha value
                    alpha = max(alpha, best_eval)

                    # If alpha is greater than beta, we can prune the branch
                    if alpha >= beta:
                        break

            # After going through all the columns, return the best evaluation
            return best_eval



        # Recursive case 2:
        # -------------------------------------------------

        # If we are evaluation the score based on how the opponent would act
        else: 

            # Initialize the worst evaluation so far with infinity
            worst_eval = np.inf

            # Get Opponent ID by swapping assigning 1 if current player is 2 else 2
            opp: int = 1 if self.player_id == 2 else 2

            # Go through all the columns
            for col in range(board.width):
                # If we can still place a piece in this column
                if board.is_valid(col):
                    # Create a new board (child node) with the hypothetical move for this column for the opponent
                    child: Board = board.get_new_board(col, opp)
                        
                    # Get the value for the child by calling the function recursively with depth -1 and is_maximising False
                    child_eval: int = self.alphabeta(child, depth -1, True, alpha, beta)

                    # If the child evaluation is better than the best evaluation so far, update the best evaluation
                    if child_eval < worst_eval:
                        worst_eval = child_eval

                    # Update the beta value
                    beta = min(beta, worst_eval)

                    # If beta is less than alpha, we can prune the branch
                    if beta <= alpha:
                        break

            # After going through all the columns, return the worst evaluation (which is the best for the player)
            return worst_eval


class HumanPlayer(PlayerController):
    """Class for the human player
    Inherits from Playercontroller
    """
    def __init__(self, player_id: int, game_n: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            heuristic (Heuristic): heuristic used by the player
        """
        super().__init__(player_id, game_n, heuristic)

    
    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        print(board)

        if self.heuristic is not None:
            print(f'Heuristic {self.heuristic} calculated the best move is:', end=' ')
            print(self.heuristic.get_best_action(self.player_id, board) + 1, end='\n\n')

        col: int = self.ask_input(board)

        print(f'Selected column: {col}')
        return col - 1
    

    def ask_input(self, board: Board) -> int:
        """Gets the input from the user

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        try:
            col: int = int(input(f'Player {self}\nWhich column would you like to play in?\n'))
            assert 0 < col <= board.width
            assert board.is_valid(col - 1)
            return col
        except ValueError: # If the input can't be converted to an integer
            print('Please enter a number that corresponds to a column.', end='\n\n')
            return self.ask_input(board)
        except AssertionError: # If the input matches a full or non-existing column
            print('Please enter a valid column.\nThis column is either full or doesn\'t exist!', end='\n\n')
            return self.ask_input(board)
        