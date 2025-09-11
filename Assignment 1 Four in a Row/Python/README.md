## Four in a Row (Connect-N) — Python

A simple, typed Python implementation of Four in a Row (Connect-N) with a pluggable heuristic and player architecture. Includes scaffolding for MinMax and Alpha-Beta players, and JIT-accelerated win detection for speed.

### Quick start

- **Python**: 3.10+ recommended. Create a virtual environment, then install deps.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Edit `app.py` to change board size and the connect target:

```python
game_n = 4  # n in a row required to win
width = 7
height = 6
```

### How to play

- The default setup is Human vs Human. Columns are 1-indexed in the prompt.
- On each turn the board is printed; if a heuristic is attached, a suggested best move is shown.
- The game ends when a player connects `n` in a row or the board is full (draw).

### Project structure

- `app.py`: Game loop, player orchestration, and fast win detection.
- `board.py`: `Board` class and core board operations.
- `players.py`: Player base class plus `HumanPlayer`, `MinMaxPlayer` (scaffold), `AlphaBetaPlayer` (scaffold).
- `heuristics.py`: Heuristic base class and `SimpleHeuristic` implementation.
- `requirements.txt`: Minimal dependencies (`numpy`, `numba`).

### Architecture overview

#### app.py

- `start_game(game_n, board, players)`: Main loop.
  - Repeatedly asks current player for a move (`make_move`).
  - Applies the move via `board.play(col, player_id)`; retries on invalid moves.
  - Checks terminal status using `winning(state, game_n)`.
  - At the end, prints the final board and each player's evaluation count.
- `winning(state, game_n)`: JIT-compiled with Numba for performance.
  - Scans vertical, horizontal, ascending and descending diagonals.
  - Returns: `1` or `2` if a player won, `-1` for draw, `0` otherwise.
- `get_players(game_n)`: Builds two players (defaults to two `HumanPlayer`s) and asserts valid setup.

#### board.py

- `Board` constructor supports:
  - `(width, height)` → empty board
  - `(other_board)` → deep copy
  - `(np.ndarray state)` → from explicit state
- Key methods:
  - `get_value(col, row)`: Value at position.
  - `get_board_state()`: Returns a copy of the current `np.ndarray` state.
  - `play(col, player_id)`: Mutates current board; drops a disc if space available.
  - `is_valid(col)`: True if the column has space.
  - `get_new_board(col, player_id)`: Returns a new `Board` with the hypothetical move applied (does not mutate current board).
  - `__str__()`: Pretty, human-readable board with `X` for player 1 and `O` for player 2.

#### players.py

- `PlayerController`: Abstract base with `make_move(board) -> int`, `get_eval_count()`, and display via `__str__`.
- `HumanPlayer`:
  - Prints board every turn and (optionally) a heuristic suggestion.
  - Prompts until a valid, 1-indexed column is entered; returns a 0-indexed column to the engine.
- `MinMaxPlayer` (scaffold):
  - Includes a worked depth-1 example and a note on using `heuristic.get_best_action` as a helper.
  - Intended to be extended with an explicit game tree and MinMax search to `depth`.
- `AlphaBetaPlayer` (scaffold):
  - Same interface as `MinMaxPlayer`; implement MinMax with alpha-beta pruning.

#### heuristics.py

- `Heuristic` base:
  - `get_best_action(player_id, board)`: One-ply scan over valid columns using `evaluate_board`.
  - `evaluate_board(player_id, board)`: Increments `eval_count`, computes utility via `_evaluate`.
  - `winning(state, game_n)`: Delegates to `app.winning` to avoid code duplication; imported lazily to prevent circular imports.
- `SimpleHeuristic`:
  - JIT-compiled `_evaluate(player_id, state, winner)`.
  - Returns a large positive/negative score for win/loss, `0` for draw, otherwise the maximum contiguous run length of the current player's discs.

### Extending the AI

Use `board.get_new_board(col, player_id)` to expand a game tree without mutating the current node. At leaf nodes or when a terminal state is detected (via `Heuristic.winning(state, game_n)`/`app.winning`), score with `heuristic.evaluate_board(player_id, board)`.

Example: swapping in a MinMax player (once implemented) in `get_players` of `app.py`:

```python
heuristic1 = SimpleHeuristic(game_n)
heuristic2 = SimpleHeuristic(game_n)
players = [
    MinMaxPlayer(1, game_n, depth=4, heuristic=heuristic1),
    HumanPlayer(2, game_n, heuristic=heuristic2),
]
```

### Notes on performance

- First calls to Numba-jitted functions (`winning`, `SimpleHeuristic._evaluate`) include JIT compile time; subsequent calls are much faster.
- The heuristic keeps an `eval_count` counter which is reported at the end of the game.

### Troubleshooting

- If Numba wheels are not available for your Python version/OS, ensure you are on a supported Python version and reinstall:

```bash
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```


