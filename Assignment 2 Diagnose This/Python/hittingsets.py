import itertools


# -------------------------------------------HS TREE------------------------------------------------

def run_hitting_set_algorithm(conflict_sets):
    """
    Algorithm that handles the entire process from conflict sets to hitting sets

    :param conflict_sets: list of conflict sets as list
    :return: the hitting sets and minimal hitting sets as list of lists
    """
    hitting_sets = conflict_sets
    minimal_hitting_sets = conflict_sets
    return hitting_sets, minimal_hitting_sets




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
