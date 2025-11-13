"""
Simple script to test all 3 heuristics with custom conflict sets.
"""

from hittingsets import run_hitting_set_algorithm

# ============================================================================
# DEFINE YOUR CUSTOM CONFLICT SETS HERE
# ============================================================================

custom_conflict_sets = [
    ['C', 'D', 'E'],               # Size 3
    ['A', 'C', 'F', 'G', 'H'],    # Size 5
    ['A', 'B'],                    # Size 2
    ['B', 'D', 'F'],               # Size 3
]

# Or try these other examples:
# custom_conflict_sets = [
#     ['A'],                      # Singleton
#     ['B', 'C'],                 # Size 2
#     ['D', 'E', 'F'],           # Size 3
#     ['G', 'H', 'I', 'J'],      # Size 4
# ]

# ============================================================================
# TEST ALL HEURISTICS
# ============================================================================

heuristics = ["smallest", "most_frequent", "random"]

print("=" * 80)
print("Testing All Heuristics with Custom Conflict Sets")
print("=" * 80)
print(f"\nConflict sets: {custom_conflict_sets}")
print(f"Conflict sizes: {[len(cs) for cs in custom_conflict_sets]}\n")

results = {}

for heuristic in heuristics:
    hitting_sets, minimal_hitting_sets, nodes_visited, elapsed_time = \
        run_hitting_set_algorithm(custom_conflict_sets, heuristic=heuristic)
    
    # Sort for consistent comparison
    minimal_hitting_sets_sorted = sorted([sorted(hs) for hs in minimal_hitting_sets])
    
    results[heuristic] = {
        'nodes_visited': nodes_visited,
        'elapsed_time': elapsed_time,
        'hitting_sets_count': len(hitting_sets),
        'minimal_hitting_sets_count': len(minimal_hitting_sets),
        'minimal_hitting_sets': minimal_hitting_sets_sorted
    }

# ============================================================================
# PRINT COMPARISON TABLE
# ============================================================================

print(f"{'Heuristic':<20} {'Nodes Visited':<15} {'Time (ms)':<15} {'Minimal HS':<15}")
print("-" * 80)

for heuristic in heuristics:
    r = results[heuristic]
    print(f"{heuristic:<20} {r['nodes_visited']:<15} "
          f"{r['elapsed_time']*1000:>10.2f}ms     {r['minimal_hitting_sets_count']:<15}")

# Calculate differences
min_nodes = min(r['nodes_visited'] for r in results.values())
max_nodes = max(r['nodes_visited'] for r in results.values())
diff = max_nodes - min_nodes
diff_percent = (diff / min_nodes * 100) if min_nodes > 0 else 0

print(f"\n→ Variation: {diff} nodes ({diff_percent:.1f}% difference)")

if diff_percent < 10:
    print("  ⚠️  Small difference")
elif diff_percent < 30:
    print("  ✓  Moderate difference")
else:
    print("  ✓✓  Large difference!")

# ============================================================================
# PRINT MINIMAL HITTING SETS FOR COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("MINIMAL HITTING SETS COMPARISON")
print("=" * 80)

# Check if all heuristics found the same sets
all_sets = [set(tuple(hs) for hs in r['minimal_hitting_sets']) for r in results.values()]
all_same = all(s == all_sets[0] for s in all_sets)

if all_same:
    print("\n✓ All heuristics found the same minimal hitting sets!")
    print(f"\nMinimal hitting sets ({len(results['smallest']['minimal_hitting_sets'])}):")
    for i, mhs in enumerate(results['smallest']['minimal_hitting_sets'], 1):
        print(f"  {i}. {mhs}")
else:
    print("\n⚠️  Different heuristics found different sets (this shouldn't happen if algorithm is correct!)")
    for heuristic in heuristics:
        print(f"\n{heuristic.upper()} found {len(results[heuristic]['minimal_hitting_sets'])} minimal hitting sets:")
        for i, mhs in enumerate(results[heuristic]['minimal_hitting_sets'], 1):
            print(f"  {i}. {mhs}")

print("\n" + "=" * 80)

# Explanation note
if not all_same:
    print("\nNOTE: If different heuristics find different numbers of minimal hitting sets,")
    print("this may indicate an issue with the algorithm or pruning logic.")
    print("All heuristics should find the same minimal hitting sets (the complete set).")
    print("Different exploration order might affect when supersets are pruned.")

print("\n")

