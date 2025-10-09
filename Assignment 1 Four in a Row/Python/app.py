# Taro Kinoshita s1140213
# Felix Mrak s1145815


from heuristics import Heuristic, SimpleHeuristic, IntermediateHeuristic #, AdvancedHeuristic
from players import PlayerController, HumanPlayer, MinMaxPlayer, AlphaBetaPlayer
from board import Board
from typing import List
import numpy as np
import time


# =============================================================================
# CONFIGURATION
# =============================================================================

# General game settings
GAME_CONFIG = {
    'GAME_N': 4,    # N in a row required to win
    'WIDTH': 6,     # Width of the board
    'HEIGHT': 6     # Height of the board
}

# Player X configuration
PLAYER_X_CONFIG = {
    'TYPE': 'Minimax',      # Type of Player (Human, Minimax, Alphabeta)
    'DEPTH': 5,             # If applicable (for Minimax/Alphabeta)
    'HEURISTIC': 'Intermediate'   # Type of heuristic (Simple, Intermediate)
}

# Player O configuration
PLAYER_O_CONFIG = {
    'TYPE': 'Alphabeta',    # Type of Player (Human, Minimax, Alphabeta)
    'DEPTH': 7,             # If applicable (for Minimax/Alphabeta)
    'HEURISTIC': 'Intermediate'   # Type of heuristic (Simple, Intermediate)
}

CLEAR_SCREEN = False

# Note: You can toggle randomness in players.py to prevent left bias

# =============================================================================



def clear_screen():
        print("\033c", end="") #end="" to not print a newline

def start_game(game_n: int, board: Board, players: List[PlayerController]) -> int:
    """Starting a game and handling the game logic

    Args:
        game_n (int): n in a row required to win
        board (Board): board to play on
        players (List[PlayerController]): players of the game

    Returns:
        int: id of the winning player, or -1 if the game ends in a draw
    """
    RED: str = '\033[31m'
    BLUE: str = '\033[34m'
    RESET: str = '\033[0m'

    print('Start game!')
    current_player_index: int = 0 # index of the current player in the players list
    winner: int = 0
    # Track previous turn's evals for each player
    prev_turn_evals: list[int] = [0, 0]
    turn_number: int = 1
    # Lists to store all eval counts per turn for each player
    player_eval_history: list[list[int]] = [[], []]

    # Main game loop
    while winner == 0:
        if CLEAR_SCREEN:
            clear_screen() # clear screen before showing the new board
        print(board)
        print("") # Empty line to keep styling consistent
        # Print current total evals and eval history (skip first turn)
        if turn_number > 1:
            for p in players:
                if p.player_id == 1: # If its player X
                    print(f'Player {RED}{p}{RESET} evaluated a boardstate {RED}{p.get_eval_count()}{RESET} times!')
                else:
                    print(f'Player {BLUE}{p}{RESET} evaluated a boardstate {BLUE}{p.get_eval_count()}{RESET} times!')
            print("") # Empty line to keep styling consistent
            print(f'Eval history - Player {RED}{players[0]}: {player_eval_history[0]}{RESET}')
            print(f'Eval history - Player {BLUE}{players[1]}: {player_eval_history[1]}{RESET}')

        current_player: PlayerController = players[current_player_index]
        before_evals: int = current_player.get_eval_count()
        move: int = current_player.make_move(board)

        while not board.play(move, current_player.player_id):
            move = current_player.make_move(board)

        # Add a small delay to show the move before continuing (increases as game progresses)
        time.sleep(turn_number * 0.005)


        # Store evals used this turn for next turn's display and add to history
        turn_evals = current_player.get_eval_count() - before_evals
        prev_turn_evals[current_player_index] = turn_evals
        player_eval_history[current_player_index].append(turn_evals)
        turn_number += 1

        current_player_index = 1 - current_player_index
        winner = winning(board.get_board_state(), game_n)

    # Printing out winner, final board and number of evaluations after the game
    if CLEAR_SCREEN:
        clear_screen() # clear screen before showing the final board
    print(board)

    if winner < 0:
        print('Game is a draw!')
    else:
        print(f'Player {current_player} won!')

    for p in players:
        if p.player_id == 1: # If its player X
            print(f'Player {RED}{p}{RESET} evaluated a boardstate {RED}{p.get_eval_count()}{RESET} times!')
        else:
            print(f'Player {BLUE}{p}{RESET} evaluated a boardstate {BLUE}{p.get_eval_count()}{RESET} times!')

    # Print complete eval history for both players
    print(f'\nEval history - Player {RED}{players[0]}: {player_eval_history[0]}{RESET}')
    print(f'Eval history - Player {BLUE}{players[1]}: {player_eval_history[1]}{RESET}')

    return winner


def winning(state: np.ndarray, game_n: int) -> int:
    """Determines whether a player has won, and if so, which one

    Args:
        state (np.ndarray): the board to check
        game_n (int): n in a row required to win

    Returns:
        int: 1 or 2 if the respective player won, -1 if the game is a draw, 0 otherwise
    """
    player: int
    counter: int

    # Vertical check
    for col in state:
        counter = 0
        player = -1
        for field in col[::-1]:
            if field == 0:
                break
            elif field == player:
                counter += 1
                if counter >= game_n:
                    return player
            else:
                counter = 1 
                player = field
            
    # Horizintal check
    for row in state.T:
        counter = 0
        player = -1
        for field in row:
            if field == 0:
                counter = 0
                player = -1
            elif field == player:
                counter += 1
                if counter >= game_n:
                    return player
            else:
                counter = 1
                player = field

    # Ascending diagonal check
    for i, col in enumerate(state[:- game_n + 1]):
        for j, field in enumerate(col[game_n - 1:]):
            if field == 0:
                continue
            player = field
            for x in range(game_n):
                if state[i + x, j + game_n - 1 - x] != player:
                    player = -1
                    break
            if player != -1:
                return player
            
    # Descending diagonal check
    for i, col in enumerate(state[game_n - 1:]):
        for j, field in enumerate(col[game_n - 1:]):
            if field == 0:
                continue
            player = field
            for x in range(game_n):
                if state[i + game_n - 1 - x, j + game_n - 1 - x] != player:
                    player = -1
                    break
            if player != -1:
                return player
        
    # Check for a draw
    if np.all(state[:, 0]):
        return -1 # The board is full, game is a draw

    return 0 # Game is not over 
    

def get_players() -> List[PlayerController]:
    """Gets the two players based on configuration

    Raises:
        AssertionError: if the players are incorrectly initialised

    Returns:
        List[PlayerController]: list with two players
    """
    game_n = GAME_CONFIG['GAME_N']

    # Create heuristics based on config
    def create_heuristic(heuristic_type: str) -> Heuristic:
        if heuristic_type == 'Simple':
            return SimpleHeuristic(game_n)
        elif heuristic_type == 'Intermediate':
            return IntermediateHeuristic(game_n)
        # elif heuristic_type == 'Advanced':
        #     return AdvancedHeuristic(game_n)
        else:
            raise ValueError(f"unknown heuristic type: {heuristic_type}")

    # Create players based on config
    def create_player(player_id: int, config: dict) -> PlayerController:
        player_type = config['TYPE']
        depth = config['DEPTH']

        if player_type == 'Human':
            return HumanPlayer(player_id, game_n, create_heuristic(config['HEURISTIC']))
        elif player_type == 'Minimax':
            return MinMaxPlayer(player_id, game_n, depth, create_heuristic(config['HEURISTIC']))
        elif player_type == 'Alphabeta':
            return AlphaBetaPlayer(player_id, game_n, depth, create_heuristic(config['HEURISTIC']))
        else:
            raise ValueError(f"unknown player type: {player_type}")

    player1 = create_player(1, PLAYER_X_CONFIG)
    player2 = create_player(2, PLAYER_O_CONFIG)

    players = [player1, player2]

    assert players[0].player_id in {1, 2}, 'The player_id of the first player must be either 1 or 2'
    assert players[1].player_id in {1, 2}, 'The player_id of the second player must be either 1 or 2'
    assert players[0].player_id != players[1].player_id, 'The players must have an unique player_id'
    assert players[0].heuristic is not players[1].heuristic, 'The players must have an unique heuristic'
    assert len(players) == 2, 'Not the correct amount of players'

    return players


if __name__ == '__main__':
    # Check whether the game_n is possible
    game_n = GAME_CONFIG['GAME_N']
    width = GAME_CONFIG['WIDTH']
    height = GAME_CONFIG['HEIGHT']
    assert 1 < game_n <= min(width, height), 'game_n is not possible'

    board: Board = Board(width, height)
    

    # # ========================================
    # # START DEBUG (remove)
    # # ========================================

    # board_array = np.array([
    #     [0, 0, 0, 0, 1, 1],  # Column 1 
    #     [0, 0, 0, 0, 0, 0],  # Column 2
    #     [0, 0, 0, 0, 0, 2],  # Column 3 
    #     [0, 0, 0, 0, 0, 2],  # Column 4
    #     [0, 0, 0, 0, 0, 2],  # Column 5
    #     [0, 0, 0, 0, 0, 1],  # Column 6
    # ])
    # board = Board(board_array)

    # # ========================================
    # # END DEBUG
    # # ========================================

    start_game(game_n, board, get_players())
    