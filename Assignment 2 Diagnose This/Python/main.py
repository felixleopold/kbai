from circuitplotter import plot_circuit
from guesscomponentsgame import choose_components, score_function
from conflictsets import ConflictSetRetriever
from hittingsets import run_hitting_set_algorithm, run_brute_force_algorithm
from colorizer import colorize_sets
from os.path import join

# ============================================================================
# CONFIGURATION
# ============================================================================
# Algorithm options: "brute_force", "hs_tree"
ALGORITHM = "brute_force"

# Document options: "circuit1.txt", "circuit2.txt", "circuit3.txt", etc.
DOCUMENT = "circuit1.txt"

# # Heuristic options: "smallest", "most_frequent", "random"
# HEURISTIC = "smallest"

# Game mode: Set to True to play the interactive game
GAME = False
# ============================================================================

if __name__ == '__main__':

    document = DOCUMENT
    game = GAME
    
    # Select algorithm based on configuration
    if ALGORITHM == "brute_force":
        algorithm_func = run_brute_force_algorithm
    else:  # Default to hs_tree
        algorithm_func = run_hitting_set_algorithm

    # It only makes sense to play the game if you have the hitting set algorithm implemented.
    if game:
        # If you play the game, choose conflict sets, compute hitting sets:
        plot_circuit(document)
        chosen_conflict_sets = choose_components()
        print(f"\nYour chosen conflict sets ({len(chosen_conflict_sets)}):")
        print(f"  {colorize_sets(chosen_conflict_sets)}")
        chosen_hitting_sets, chosen_minimal_hitting_sets = algorithm_func(chosen_conflict_sets)
        print(f"\nYour hitting sets ({len(chosen_hitting_sets)}):")
        print(f"  {colorize_sets(chosen_hitting_sets)}")
        print(f"\nYour minimal hitting sets ({len(chosen_minimal_hitting_sets)}):")
        print(f"  {colorize_sets(chosen_minimal_hitting_sets)}")

    # Collect conflict sets:
    csr = ConflictSetRetriever(join("circuits", document))
    conflict_sets = csr.retrieve_conflict_sets()
    print(f"\nActual conflict sets ({len(conflict_sets)}):")
    print(f"  {conflict_sets}")

    # Collect minimal hitting sets:
    if len(conflict_sets) == 0:
        print("This circuit works correctly, there are no faulty components!")
    else:
        hitting_sets, minimal_hitting_sets = algorithm_func(conflict_sets)
        print(f"\nHitting sets ({len(hitting_sets)}):")
        print(f"  {colorize_sets(hitting_sets)}")
        print(f"\nMinimal hitting sets ({len(minimal_hitting_sets)}):")
        print(f"  {colorize_sets(minimal_hitting_sets)}")

    # Give score on similarity between the two sets:
    if game:
        score = score_function(conflict_sets, chosen_conflict_sets)
        print(f"Your score: {score:.2f}%")