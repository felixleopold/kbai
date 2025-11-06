import itertools


# -------------------------------------------HS TREE------------------------------------------------

def hits_conflict(path_labels: list[str], conflict_set: list[str]) -> bool:
    """
    Check if a path (set of components) hits a conflict set.
    A path hits a conflict set if they have at least one element in common.
    
    Returns:
    True if path_labels intersects conflict_set, False otherwise
    """
    return any(component in conflict_set for component in path_labels)


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


def run_hitting_set_algorithm(conflict_sets):
    """
    Algorithm that handles the entire process from conflict sets to hitting sets

    :param conflict_sets: list of conflict sets as list
    :return: the hitting sets and minimal hitting sets as list of lists


    Idea:
    1. Start with an empty root node (path_labels = [])
    2. Pick the smallest conflict set to expand first
    3. Create a child node for each component in the conflict set
    4. For each child, check which conflicts are still uncovered
    5. If all conflicts are hit, mark as solution
    6. Otherwise, pick the next smallest uncovered conflict and expand
    7. Repeat until all nodes are processed (BFS)
    8. Collect all solutions and filter to minimal hitting sets
    """
    hitting_sets = conflict_sets
    minimal_hitting_sets = conflict_sets
    return hitting_sets, minimal_hitting_sets


class HSNode:
    """
    Node class for the HS Tree

    Attributes:
    path_labels: list of components hit so far
    is_solution: bool

    Methods:
    create_children: create child nodes for a conflict set
    check_is_solution: check if the node is a solution
    set_solution: set the node to a solution
    __str__: print the node
    """

    def __init__(self, path_labels: list[str], is_solution: bool = False):
        self.path_labels = path_labels
        self.is_solution = is_solution

    def create_children(self, conflict_set: list[str]) -> list['HSNode']:
        """
        Create child nodes for each component in the conflict set.
        Only creates children for components not already in the path.
        """
        children = []
        for component in conflict_set:
            if component not in self.path_labels:
                children.append(HSNode(self.path_labels + [component], False))
        return children

    def check_is_solution(self) -> bool:
        """
        Check if this node is marked as a solution.
        """
        return self.is_solution

    def set_solution(self) -> None:
        """Mark this node as a solution (hitting set)."""
        self.is_solution = True

    def __str__(self) -> str:
        return f"HSNode (path_labels={self.path_labels}, is_solution={self.is_solution})"


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
    
    # Filter to minimal hitting sets, so remove supersets
    minimal_hitting_sets = []
    for hitting_set in hitting_sets:
        is_minimal = True
        hitting_set_set = set(hitting_set)
        
        # Check if any other hitting set is a strict subset
        for others in hitting_sets:
            others_set = set(others)
            if others_set < hitting_set_set:  # Strict subset
                is_minimal = False
                break
        
        if is_minimal:
            minimal_hitting_sets.append(hitting_set)
    
    return hitting_sets, minimal_hitting_sets
