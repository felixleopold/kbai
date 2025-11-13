from circuitplotter import plot_circuit
from guesscomponentsgame import choose_components, score_function
from conflictsets import ConflictSetRetriever
from hittingsets import run_hitting_set_algorithm, run_brute_force_algorithm
from os.path import join

# ============================================================================
# CONFIGURATION
# ============================================================================
# Algorithm options: "brute_force", "hs_tree"
ALGORITHM = "hs_tree"

# Document options: "circuit1.txt", "circuit2.txt", "circuit3.txt", etc.
DOCUMENT = "circuit8.txt"

# # Heuristic options: "smallest", "most_frequent", "random"
HEURISTIC = "smallest"

# Game mode:
GAME = False
# ============================================================================

if __name__ == '__main__':

    document = DOCUMENT
    game = GAME

    # Print configg information
    print(f"Circuit: {document}")
    print(f"Heuristic: {HEURISTIC}")

    # Plot the circuit
    # plot_circuit(document)
    
    # It only makes sense to play the game if you have the hitting set algorithm implemented.
    if game:
        # If you play the game, choose conflict sets, compute hitting sets:
        chosen_conflict_sets = choose_components()
        print(f"\nYour chosen conflict sets ({len(chosen_conflict_sets)}):")
        print(f"  {chosen_conflict_sets}")
        
        # Compute hitting sets using the selected algorithm
        if ALGORITHM == "brute_force":
            chosen_hitting_sets, chosen_minimal_hitting_sets = run_brute_force_algorithm(chosen_conflict_sets)
        else:  # hs_tree
            chosen_hitting_sets, chosen_minimal_hitting_sets, nodes_visited, elapsed_time = run_hitting_set_algorithm(chosen_conflict_sets, heuristic=HEURISTIC)
            print(f"Nodes visited: {nodes_visited}")
            print(f"Execution time: {elapsed_time*1000:.2f}ms")
        
        print(f"\nYour hitting sets ({len(chosen_hitting_sets)}):")
        print(f"  {chosen_hitting_sets}")
        print(f"\nYour minimal hitting sets ({len(chosen_minimal_hitting_sets)}):")
        print(f"  {chosen_minimal_hitting_sets}")

    # Collect conflict sets:
    csr = ConflictSetRetriever(join("circuits", document))
    conflict_sets = csr.retrieve_conflict_sets()
    print(f"\nActual conflict sets ({len(conflict_sets)}):")
    print(f"  {conflict_sets}")

    # Collect minimal hitting sets:
    if len(conflict_sets) == 0:
        print("This circuit works correctly, there are no faulty components!")
    else:
        # Compute hitting sets using the selected algorithm
        if ALGORITHM == "brute_force":
            hitting_sets, minimal_hitting_sets = run_brute_force_algorithm(conflict_sets)
        else:  # hs_tree
            hitting_sets, minimal_hitting_sets, nodes_visited, elapsed_time = run_hitting_set_algorithm(conflict_sets, heuristic=HEURISTIC)
            print(f"Nodes visited: {nodes_visited}")
            print(f"Execution time: {elapsed_time*1000:.2f}ms")
        print(f"\nHitting sets ({len(hitting_sets)}):")
        print(f"  {hitting_sets}")
        print(f"\nMinimal hitting sets ({len(minimal_hitting_sets)}):")
        print(f"  {minimal_hitting_sets}")

    # Give score on similarity between the two sets:
    if game:
        score = score_function(conflict_sets, chosen_conflict_sets)
        print(f"Your score: {score:.2f}%")