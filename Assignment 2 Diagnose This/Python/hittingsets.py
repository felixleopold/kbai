import itertools
import random
import time

from z3 import K

# -------------------------------------------CLASS------------------------------------------------
class HSNode:
    """
    Node class for the HS Tree

    Attributes:
    path_labels: list of components hit so far
    is_solution: bool

    Methods:
    create_children: create child nodes for a conflict set
    set_solution: set the node to a solution
    __str__: print the node
    """

    def __init__(self, path_labels: list[str], is_solution: bool = False):
        self.path_labels = path_labels
        self.is_solution = is_solution
        # children

    def create_children(self, selected_conflict_set: list[str]) -> list['HSNode']:
        """
        Create child nodes for each component in the conflict set.
        Only creates children for components not already in the path.
        """
        children = []
        for component in selected_conflict_set:
            if component not in self.path_labels:
                children.append(HSNode(self.path_labels + [component], False))
        return children

    def set_solution(self) -> None:
        """Mark this node as a solution (hitting set)."""
        self.is_solution = True

    def __str__(self) -> str:
        return f"HSNode (path_labels={self.path_labels}, is_solution={self.is_solution})"

# -------------------------------------------HELPER------------------------------------------------

def hits_conflict(path_labels: list[str], conflict_set: list[str]) -> bool:
    """
    Check if a path (set of components) hits a conflict set.
    A path hits a conflict set if they have at least one element in common.
    
    Returns:
    True if path_labels intersects conflict_set, False otherwise
    """
    for component in path_labels:
        if component in conflict_set:
            return True
    return False


def get_uncovered_conflicts(path_labels: list[str], conflict_sets: list[list[str]]) -> list[list[str]]:
    """
    Get all conflict sets that are not yet hit by the current path.
    
    Returns:
    List of conflict sets that are not hit by path_labels
    """
    uncovered = []
    for conflict in conflict_sets:
        if not hits_conflict(path_labels, conflict):
            uncovered.append(conflict)
    return uncovered


def get_minimal_hitting_sets(hitting_sets: list[list[str]]) -> list[list[str]]:
    """
    Filter hitting sets to only include minimal hitting sets.
    A minimal hitting set is one that has no strict subset that is also a hitting set.
    
    Parameters:
    hitting_sets: List of all hitting sets
    
    Returns:
    List of minimal hitting sets (supersets and duplicates removed)
    """
    # Remove duplicates first
    seen = set()
    unique_hitting_sets = []
    for hitting_set in hitting_sets:
        key = tuple(sorted(hitting_set))
        if key not in seen:
            seen.add(key)
            unique_hitting_sets.append(hitting_set)
    
    # Filter to minimal hitting sets (remove supersets)
    minimal_hitting_sets = []
    for hitting_set in unique_hitting_sets:
        is_minimal = True
        hitting_set_set = set(hitting_set)
        
        # Check if any other hitting set is a strict subset
        for others in unique_hitting_sets:
            others_set = set(others)
            if others_set < hitting_set_set:  # Strict subset
                is_minimal = False
                break
        
        if is_minimal:
            minimal_hitting_sets.append(hitting_set)
    
    return minimal_hitting_sets

# ------------------------------------------HEURISTICS-----------------------------------------------

def select_smallest_conflict(uncovered_conflicts: list[list[str]]) -> list[str]:
    """
    Heuristic: Select the conflict with the fewest components
    This minimizes the branching factor.
    """
    return min(uncovered_conflicts, key=len)


def select_random_conflict(uncovered_conflicts: list[list[str]]) -> list[str]:
    """
    Heuristic: Select a random conflict from the uncovered conflicts
    Useful for baseline comparison
    """
    return random.choice(uncovered_conflicts)


def select_most_frequent_component_conflict(uncovered_conflicts: list[list[str]]) -> list[str]:
    """
    Heuristic: Select the first conflict containing the most frequent component from all uncovered conflicts
    
    Idea: Components appearing in many conflicts are more likely to be part of minimal hitting sets
    Returns the first conflict (in order) that contains the most frequent component
    """
    # Count how often each component appears in all uncovered conflicts
    component_counts = {}
    for conflict in uncovered_conflicts:
        for component in conflict:
            component_counts[component] = component_counts.get(component, 0) + 1
    
    # Find the most frequent component
    most_frequent_component = max(component_counts, key=component_counts.get)
    
    # Find conflicts with the most frequent component
    conflicts_with_most_frequent = [conflict for conflict in uncovered_conflicts if most_frequent_component in conflict]
    
    # Return the first conflict found (not the smallest)
    return conflicts_with_most_frequent[0]


# Heuristic names to functions
HEURISTICS = {
    "smallest": select_smallest_conflict,
    "most_frequent": select_most_frequent_component_conflict,
    "random": select_random_conflict
}

# -------------------------------------------HS TREE------------------------------------------------

def hs_tree_recursive(node: HSNode, conflict_sets: list[list[str]], solutions: list[list[str]], heuristic_func, visit_count: list[int]) -> None:

        # Count every node visit (includes solutions, pruned nodes, and expanded nodes)
        visit_count[0] += 1

        uncovered_conflicts = get_uncovered_conflicts(node.path_labels, conflict_sets)

        # BASE CASE: All conflicts are covered, so we have reaced a solution
        if not uncovered_conflicts:
            node.set_solution()
            solutions.append(node.path_labels.copy())
            return # Stop expanding

        # PRUNING: Check if current path if a superset of a solution
        for solution in solutions:
            if set(solution) <= set(node.path_labels):
                return # Prune by returning

        selected_conflict = heuristic_func(uncovered_conflicts)

        # RECURSIVE CASE: Explore each component in the selected conflict
        children = node.create_children(selected_conflict)
        for child in children:
            hs_tree_recursive(child, conflict_sets, solutions, heuristic_func, visit_count)

def run_hitting_set_algorithm(conflict_sets, heuristic="smallest"):
    """
    Algorithm that handles the entire process from conflict sets to hitting sets

    :param conflict_sets: list of conflict sets as list
    :return: the hitting sets and minimal hitting sets as list of lists


    Idea:
    1. Start with an empty root node (no path_labels)
    2. Pick the smallest (for example) conflict set to expand first
    3. Create a child node for each component in the conflict set
    4. For each child, check which conflicts are still uncovered
    5. If all conflicts are hit, mark as solution
    6. Otherwise, pick the next smallest (for example) uncovered conflict and expand
    7. Repeat until all nodes are processed
    8. Collect all solutions and filter to minimal hitting sets
    """

    heuristic_func = HEURISTICS[heuristic]

    # Measure execution time
    start_time = time.perf_counter()

    # Run recursive HS-Tree
    hitting_sets = []
    visit_count = [0]  # Use list to allow modification in recursive calls
    hs_tree_recursive(HSNode([]), conflict_sets, hitting_sets, heuristic_func, visit_count)

    # Filter to minimal hitting sets
    minimal_hitting_sets = get_minimal_hitting_sets(hitting_sets)

    elapsed_time = time.perf_counter() - start_time

    return hitting_sets, minimal_hitting_sets, visit_count[0], elapsed_time


# -----------------------------------------BRUTE FORCE----------------------------------------------

def hits_all(combo, conflict_sets):
    """
    Check if a combination hits all conflict sets
    A combination hits a conflict set if it has at least one element in common
    
    Parameters:
    combo: Tuple of components
    conflict_sets: List of conflict sets
    
    Returns:
    bool: True if combo hits all conflict sets, False otherwise
    """
    for conflict in conflict_sets:
        if not any(component in conflict for component in combo):
            return False
    return True


def run_brute_force_algorithm(conflict_sets):
    """
    Algorithm that brute-forces all hitting sets by trying all combinations of components

    :param conflict_sets: list of conflict sets as list
    :return: the hitting sets and minimal hitting sets as list of lists
    """ 
    
    components = set().union(*conflict_sets)

    # Convert to sorted list for consistent output
    components_list = sorted(list(components))
    hitting_sets = []
    
    # Try all combinations in increasing size order
    for size in range(1, len(components_list) + 1):
        for combo in itertools.combinations(components_list, size):
            if hits_all(combo, conflict_sets):
                hitting_sets.append(list(combo))
    
    # Filter to minimal hitting sets
    minimal_hitting_sets = get_minimal_hitting_sets(hitting_sets)
    
    return hitting_sets, minimal_hitting_sets
