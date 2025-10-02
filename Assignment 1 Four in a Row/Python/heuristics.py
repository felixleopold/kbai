from __future__ import annotations
import numpy as np
from abc import abstractmethod
from numba import jit
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from board import Board


class Heuristic:
    """Abstract class defining a heuristic
    """
    def __init__(self, game_n: int) -> None:
        """
        Args:
            game_n (int): n in a row required to win
        """
        self.game_n: int = game_n
        self.eval_count: int = 0


    def get_best_action(self, player_id: int, board: Board) -> int:
        """Determines the best column for the next move

        Args:
            player_id (int): the player for which to compute the heuristic value
            board (Board): the board to evaluate

        Returns:
            int: column with the best heuristic value
        """
        min_util: int = -max(board.get_board_state().shape)
        utils: np.ndarray = np.full(board.width, min_util - 1, dtype=int)

        for i in range(board.width):
            if board.is_valid(i):
                self.eval_count += 1
                utils[i] = self.evaluate_board(player_id, board.get_new_board(i, player_id))

        return np.argmax(utils)
    

    def evaluate_board(self, player_id: int, board: Board) -> int:
        """Helper function to assign a utility to a board

        Args:
            player_id (int): the player for which to compute the heuristic value
            board (Board): the board to evaluate

        Returns:
            int: the utility of a board
        """
        self.eval_count += 1
        state: np.ndarray = board.get_board_state()
        return self._evaluate(player_id, state, self.winning(state, self.game_n))
    

    @staticmethod
    def winning(state: np.ndarray, game_n: int) -> int:
        """Determines whether a player has won, and if so, which one

        Args:
            state (np.ndarray): the board to check
            game_n (int): n in a row required to win

        Returns:
            int: 1 or 2 if the respective player won, -1 if the game is a draw, 0 otherwise
        """
        from app import winning as app_winning # imported here to avoid circular imports
        return app_winning(state, game_n)
    

    def __str__(self) -> str:
        """ 
        Returns:
            str: name of the heuristic
        """
        return self._name()


    @abstractmethod
    def _name(self) -> str:
        """Abstract method for naming the heuristic

        Returns:
            str: name of the heuristic
        """
        pass


    @abstractmethod
    def _evaluate(self, player_id: int, state: np.ndarray, winner: int) -> int:
        """Abstract method for evaluating a board state

        Args:
            player_id (int): the player for which to compute the heuristic value
            state (np.ndarray): the board to check
            winner (int): 1 or 2 if the respective player won, -1 if the game is a draw, 0 otherwise

        Returns:
            int: heuristic value for the board state
        """
        pass    


class SimpleHeuristic(Heuristic):
    """A simple heuristic
    Inherits from Heuristic
    """
    def __init__(self, game_n: int) -> None:
        """
        Args:
            game_n (int): n in a row required to win
        """
        super().__init__(game_n)


    def _name(self) -> str:
        """
        Returns:
            str: the name of the heuristic; Simple
        """
        return 'Simple'
    
    
    @staticmethod
    @jit(nopython=True, cache=True)
    def _evaluate(player_id: int, state: np.ndarray, winner: int) -> int:
        """Determine utility of a board state

        Args:
            player_id (int): the player for which to compute the heuristic value
            state (np.ndarray): the board to check
            winner (int): 1 or 2 if the respective player won, -1 if the game is a draw, 0 otherwise

        Returns:
            int: heuristic value for the board state
        """
        width: int
        height: int
        width, height = state.shape

        if winner == player_id: # player won
            return max(width, height)
        elif winner < 0: # draw
            return 0
        elif winner > 0: # player lost
            return -max(width, height)
        
        # not winning or losing, return highest number of claimed squares in a row      
        max_in_row: int = 0
        for i in range(width):
            for j in range(height):
                if state[i, j] != player_id:
                    continue

                max_in_row = max(max_in_row, 1)

                for x in range(1, width - i):
                    if state[i + x, j] == player_id:
                        max_in_row = max(max_in_row, x + 1)
                    else:
                        break

                for y in range(1, height - j):
                    if state[i, j + y] == player_id:
                        max_in_row = max(max_in_row, y + 1)
                    else:
                        break

                for d in range(1, min(width - i, height - j)):
                    if state[i + d, j + d] == player_id:
                        max_in_row = max(max_in_row, d + 1)
                    else:
                        break

                for a in range(1, min(width - i, j)):
                    if state[i + a, j - a] == player_id:
                        max_in_row = max(max_in_row, a + 1)
                    else:
                        break

        return max_in_row

# Testing Heuristic
class WindowHeuristic(Heuristic):
    def _name(self) -> str:
        return "Window"

    def _evaluate(self, player_id: int, state: np.ndarray, winner: int) -> int:
        if winner == player_id:
            return 10_000
        if winner > 0 and winner != player_id:
            return -10_000
        if winner < 0:
            return 0

        opp = 1 if player_id == 2 else 2
        n = self.game_n

        # weights: tune as needed
        # index k means exactly k in a row (k < n). n is handled above as terminal.
        W = np.array([0, 1, 5, 25, 125, 750, 5000], dtype=int)  # extend if n>6
        if len(W) <= n:
            # grow geometrically to support larger n
            grow = [W[-1] * 5 ** i for i in range(n + 1 - len(W))]
            W = np.concatenate([W, np.array(grow, dtype=int)])

        def score_line(seg: np.ndarray, pid: int) -> int:
            # returns score for a length-n window
            cnt = np.count_nonzero(seg == pid)
            cnt_opp = np.count_nonzero((seg != 0) & (seg != pid))
            if cnt_opp > 0:
                return 0  # blocked window
            if cnt == 0:
                return 0  # empty window not helpful
            # open ends bonus: check cells just outside the window if exist and empty
            open_bonus = 0
            # caller provides context for open ends via closures below
            return W[cnt] + open_bonus

        H, Wd = state.shape[1], state.shape[0]  # note: your code uses state[x, y]
        # helpers to iterate windows and compute open ends
        total = 0
        for dx, dy in ((1,0), (0,1), (1,1), (1,-1)):
            x_range = range(Wd)
            y_range = range(H)
            for x0 in x_range:
                for y0 in y_range:
                    x1 = x0 + (n - 1) * dx
                    y1 = y0 + (n - 1) * dy
                    if x1 < 0 or x1 >= Wd or y1 < 0 or y1 >= H:
                        continue
                    # collect the window
                    xs = x0 + np.arange(n) * dx
                    ys = y0 + np.arange(n) * dy
                    seg = state[xs, ys]

                    # compute open ends: cells just before and after the window
                    pre_x, pre_y = x0 - dx, y0 - dy
                    post_x, post_y = x1 + dx, y1 + dy
                    pre_open = (0 <= pre_x < Wd and 0 <= pre_y < H and state[pre_x, pre_y] == 0)
                    post_open = (0 <= post_x < Wd and 0 <= post_y < H and state[post_x, post_y] == 0)
                    ends = pre_open + post_open  # 0..2

                    def window_val(pid: int) -> int:
                        cnt = np.count_nonzero(seg == pid)
                        cnt_opp = np.count_nonzero((seg != 0) & (seg != pid))
                        if cnt_opp > 0 or cnt == 0:
                            return 0
                        base = (10 ** (cnt))  # geometric growth
                        # bonus for open ends; double-open is best
                        return base * (1 + ends)

                    total += window_val(player_id)
                    total -= window_val(opp)

        # light 1-ply danger check: penalize states where opponent has an immediate winning move
        # assumes gravity and "valid columns" semantics
        try:
            from app import Board  # type: ignore
        except Exception:
            Board = None
        if Board is not None:
            # reconstruct a Board from state if your Board ctor supports it; otherwise skip
            pass  # keep heuristic pure if Board rebuild is not trivial

        return int(total)
