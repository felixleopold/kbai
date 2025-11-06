# Implementation Guide: Hitting Set Algorithm
## A Step-by-Step Thought Process

**Purpose:** This guide explains the intuition and thought process for implementing the hitting set algorithm from scratch. Use it as inspiration to build your own solution.

**Author:** Felix Mrak  
**Course:** Knowledge Based AI - Programming Assignment 2  
**Date:** November 6, 2025

---

## 📚 Table of Contents

1. [Understanding the Problem](#1-understanding-the-problem)
2. [Starting Simple: The Brute-Force Approach](#2-starting-simple-the-brute-force-approach)
3. [Optimizing: The HS-Tree Approach](#3-optimizing-the-hs-tree-approach)
4. [Adding Heuristics](#4-adding-heuristics)
5. [Testing and Debugging](#5-testing-and-debugging)
6. [Common Pitfalls](#6-common-pitfalls)

---

## 1. Understanding the Problem

### What Are We Actually Trying to Do?

**Given:** A collection of conflict sets (lists of components)  
**Goal:** Find all minimal sets that "hit" (intersect with) every conflict set

### Visual Example

```
Conflict sets: C = {{A, B}, {B, C}}

Think of it like this:
- Conflict 1: At least one of {A, B} must be faulty
- Conflict 2: At least one of {B, C} must be faulty

Possible solutions:
- {B} alone hits both ✓ MINIMAL
- {A, C} hits both ✓ MINIMAL
- {A, B} hits both but contains {B} which is also a solution ✗ NOT MINIMAL
- {B, C} hits both but contains {B} which is also a solution ✗ NOT MINIMAL
```

### Key Insight

A **hitting set** must pick at least one element from each conflict set.  
A **minimal hitting set** does this with no redundant elements.

### The Core Question

For each conflict set, ask: "Which element should I pick to cover this and possibly other conflicts?"

---

## 2. Starting Simple: The Brute-Force Approach

### The Intuition

"Let me just try every possible combination and see which ones work!"

This is like trying to unlock a safe by testing every combination. It's slow but guaranteed to work.

### Thought Process: Step by Step

#### Step 1: Understand What We're Searching

```
If I have components {A, B, C}, the possible diagnoses are:
- Size 1: {A}, {B}, {C}
- Size 2: {A,B}, {A,C}, {B,C}
- Size 3: {A,B,C}
```

**Key insight:** Start with small sets first (fewer faults = better diagnosis)

#### Step 2: Check If a Candidate "Hits" All Conflicts

```python
def does_it_hit_all_conflicts(candidate, conflict_sets):
    """
    Think: Does this candidate have at least one element from each conflict?
    """
    for conflict in conflict_sets:
        # Check if candidate and conflict have any overlap
        if no overlap between candidate and conflict:
            return False  # Failed to hit this conflict
    return True  # Hit all conflicts!
```

**Mental model:** Imagine checking boxes on a list. Each conflict is a box. Did we check them all?

#### Step 3: Generate All Combinations Systematically

```python
# Pseudo-code for the thought process

all_components = extract all unique components from all conflicts

for size in 1 to number_of_components:
    for each combination of 'size' components:
        if this combination hits all conflicts:
            add it to our list of hitting sets
```

**Why start with size 1?** Smaller = fewer faulty components = better diagnosis!

#### Step 4: Filter to Minimal Sets

Once we have all hitting sets, we need to remove non-minimal ones:

```python
# Thought process: Is this set minimal?

for each hitting_set in all_hitting_sets:
    is_this_minimal = True
    
    for each other_set in all_hitting_sets:
        if other_set is a STRICT SUBSET of hitting_set:
            # Someone else can do it with fewer components!
            is_this_minimal = False
            break
    
    if is_this_minimal:
        keep it!
```

**Mental model:** Remove any set where someone else already did the job with fewer components.

### Complete Brute-Force Thought Process

```
INPUT: conflict_sets = [[A, B], [B, C]]

STEP 1: Extract components
  → components = {A, B, C}

STEP 2: Try size 1 combinations
  Try {A}: Does it hit [A,B]? YES ✓  Does it hit [B,C]? NO ✗
  Try {B}: Does it hit [A,B]? YES ✓  Does it hit [B,C]? YES ✓ → FOUND ONE!
  Try {C}: Does it hit [A,B]? NO ✗

STEP 3: Try size 2 combinations
  Try {A,B}: Does it hit [A,B]? YES ✓  Does it hit [B,C]? YES ✓ → FOUND ONE!
  Try {A,C}: Does it hit [A,B]? YES ✓  Does it hit [B,C]? YES ✓ → FOUND ONE!
  Try {B,C}: Does it hit [A,B]? YES ✓  Does it hit [B,C]? YES ✓ → FOUND ONE!

STEP 4: Try size 3 combinations
  Try {A,B,C}: Hits all ✓ → FOUND ONE!

ALL HITTING SETS: [{B}, {A,B}, {A,C}, {B,C}, {A,B,C}]

STEP 5: Filter to minimal
  {B}: No subsets exist → MINIMAL ✓
  {A,B}: Contains {B} as subset → NOT MINIMAL ✗
  {A,C}: No subsets exist → MINIMAL ✓
  {B,C}: Contains {B} as subset → NOT MINIMAL ✗
  {A,B,C}: Contains subsets → NOT MINIMAL ✗

MINIMAL HITTING SETS: [{B}, {A,C}]
```

### When to Use Brute-Force

**Advantages:**
- Simple to understand and implement
- Guaranteed correct
- Good for small problems (< 10 components)
- Perfect for verifying other methods

**Disadvantages:**
- Exponential time: O(2^n)
- Wastes time on non-minimal sets
- Doesn't scale to large problems

**Pro tip:** Always implement brute-force first! It's your "ground truth" for testing.

---

## 3. Optimizing: The HS-Tree Approach

### The Intuition

"Instead of trying every combination, let me build a tree that explores only promising paths and prunes dead ends."

Think of it like a GPS that avoids routes it knows will take longer.

### The Big Idea: Reiter's HS-Tree

**Key insight:** Build a tree where:
- Each node represents a partial diagnosis (components chosen so far)
- Edges are labeled with components
- Leaves are complete diagnoses

**Visual Example:**

```
Conflict sets: C = {{A, B}, {B, C}}

Tree structure:
                    ROOT (∅)
                   /    \
                  A      B  ← Pick from first conflict {A,B}
                 / \      |
                C   ✗    LEAF (diagnosis = {B})
               /         
           LEAF ({A,C})   

✗ = pruned (B already in path would be redundant)
```

### Thought Process: Step by Step

#### Step 1: What Information Does Each Node Need?

```python
class TreeNode:
    path_labels        # Components chosen from root to here
    is_solution        # Does this node represent a complete diagnosis?
    
# That's it! Keep it simple.
```

**Mental model:** Each node remembers "Which components did we decide are faulty to get here?"

#### Step 2: How Do We Expand a Node?

```
At each node, ask:
1. Which conflicts are NOT yet hit by our current path?
2. Pick ONE uncovered conflict
3. Create child nodes for EACH component in that conflict
```

**Example walkthrough:**

```
Start: ROOT (path = ∅)
  Uncovered conflicts: {A,B}, {B,C}
  Pick conflict: {A,B}
  Create children: One for A, one for B

Node A (path = {A}):
  Uncovered conflicts: {B,C}  (A doesn't help here)
  Pick conflict: {B,C}
  Create children: One for B, one for C
  
Node A→C (path = {A,C}):
  Uncovered conflicts: None!
  This is a SOLUTION ✓

Node B (path = {B}):
  Uncovered conflicts: None!  (B hits both original conflicts)
  This is a SOLUTION ✓
```

#### Step 3: When Do We Stop Expanding?

```python
# At each node, check:

uncovered_conflicts = find_conflicts_not_hit_by_current_path()

if uncovered_conflicts is empty:
    # All conflicts are covered!
    This node is a SOLUTION
    Don't expand further
else:
    # Still have work to do
    Pick one uncovered conflict
    Expand children for each component in it
```

**Key insight:** If your path already hits all conflicts, you're done with this branch!

#### Step 4: Pruning - The Secret Sauce

**Pruning Rule 1: Superset Check**

```
If we already found {B} is a solution,
and we're exploring path {A, B},
we can STOP! 

Why? {A,B} contains {B} which already works.
So {A,B} can never be minimal.
```

```python
def should_prune(current_path, known_solutions):
    for solution in known_solutions:
        if solution ⊆ current_path:  # solution is subset of current_path
            return True  # PRUNE!
    return False
```

**Pruning Rule 2: No Duplicates in Path**

```
When creating children from conflict {A, B, C},
if our path already contains B,
don't create a child for B (would be redundant).
```

**Mental model:** Don't go down paths you know will lead to non-minimal solutions.

#### Step 5: Use BFS for Cardinality-Minimality

**Why BFS (Breadth-First Search)?**

```
BFS explores level-by-level:
Level 1: All diagnoses of size 1
Level 2: All diagnoses of size 2
Level 3: All diagnoses of size 3
...

This means we find SMALLEST diagnoses first!
```

**Implementation:**

```python
# Use a queue (FIFO)
queue = [root_node]

while queue is not empty:
    node = queue.pop(0)  # Take from front (BFS)
    
    if should_prune(node):
        continue
    
    if all_conflicts_covered(node):
        add to solutions
    else:
        expand children
        add children to END of queue
```

**DFS would work too, but BFS is better for finding small diagnoses first.**

### Complete HS-Tree Thought Process

```
INPUT: conflict_sets = [[A, B], [B, C]]

STEP 1: Initialize
  root = Node(path = ∅)
  queue = [root]
  solutions = []

STEP 2: Process root
  Uncovered: {A,B}, {B,C}
  Select conflict: {A,B}  (could pick either)
  Create children:
    - Node_A with path = {A}
    - Node_B with path = {B}
  Queue now: [Node_A, Node_B]

STEP 3: Process Node_A (path = {A})
  Check pruning: No solutions yet, so no pruning
  Uncovered: {B,C}  (A doesn't hit this)
  Select conflict: {B,C}
  Create children:
    - Node_A_B with path = {A, B}
    - Node_A_C with path = {A, C}
  Queue now: [Node_B, Node_A_B, Node_A_C]

STEP 4: Process Node_B (path = {B})
  Check pruning: No solutions yet
  Uncovered: None!  (B hits both {A,B} and {B,C})
  → SOLUTION FOUND: {B}
  Add {B} to solutions
  Queue now: [Node_A_B, Node_A_C]

STEP 5: Process Node_A_B (path = {A, B})
  Check pruning: {B} ⊆ {A,B}? YES!
  → PRUNE this node ✂️
  Queue now: [Node_A_C]

STEP 6: Process Node_A_C (path = {A, C})
  Check pruning: {B} ⊆ {A,C}? NO
  Uncovered: None! (A hits {A,B}, C hits {B,C})
  → SOLUTION FOUND: {A,C}
  Add {A,C} to solutions
  Queue now: []

STEP 7: Queue empty, we're done!
  
SOLUTIONS: [{B}, {A,C}]
```

### Comparison: Brute-Force vs HS-Tree

**For conflict sets: {{A, B}, {B, C}}**

| Method | Combinations Tested | Nodes Expanded | Efficiency |
|--------|-------------------|----------------|------------|
| Brute-Force | 2^3 = 8 | N/A | Tests all 8 |
| HS-Tree | N/A | 6 nodes | Prunes 2 paths |

**Bigger example: 10 components**

| Method | Combinations | Result |
|--------|-------------|--------|
| Brute-Force | 2^10 = 1024 | Slow |
| HS-Tree | ~50-100 nodes | Fast with pruning |

---

## 4. Adding Heuristics

### The Problem

When expanding a node, we need to **pick one uncovered conflict** to expand.

**Question:** Which conflict should we pick?

### The Impact

Different choices lead to different tree structures and different efficiency!

### Heuristic 1: Smallest Conflict First

**Intuition:** "Pick the conflict with fewest components"

**Why?**
- Fewer components = fewer children to explore
- Reduces branching factor
- Often finds solutions faster

**Example:**

```
Uncovered conflicts: {A, B}, {C, D, E, F}

Pick {A, B} because it has only 2 components
→ Create only 2 children instead of 4
```

**Implementation thought process:**

```python
def select_conflict(uncovered_conflicts):
    # Which has fewest components?
    return min(uncovered_conflicts, key=len)
```

**When it's good:** General purpose, usually best

### Heuristic 2: Most Frequent Component

**Intuition:** "Pick the conflict containing the component that appears most often"

**Why?**
- If component X appears in many conflicts, it's probably important
- Choosing it early might cover multiple conflicts at once
- Can lead to smaller diagnoses

**Example:**

```
Uncovered conflicts: {A, B}, {B, C}, {B, D}

Component frequencies:
  B: appears 3 times
  A: appears 1 time
  C: appears 1 time
  D: appears 1 time

Pick any conflict containing B (most frequent)
```

**Implementation thought process:**

```python
def select_conflict(uncovered_conflicts):
    # Count how often each component appears
    frequency = {}
    for conflict in uncovered_conflicts:
        for component in conflict:
            frequency[component] = frequency.get(component, 0) + 1
    
    # Pick conflict with highest frequency component
    best_conflict = None
    best_freq = 0
    for conflict in uncovered_conflicts:
        max_freq_in_this_conflict = max(frequency[c] for c in conflict)
        if max_freq_in_this_conflict > best_freq:
            best_freq = max_freq_in_this_conflict
            best_conflict = conflict
    
    return best_conflict
```

**When it's good:** When components have different failure rates, or conflicts overlap heavily

### Heuristic 3: Random Selection

**Intuition:** "Just pick any conflict randomly"

**Why?**
- Baseline for comparison
- Shows the value of informed heuristics
- Sometimes surprisingly effective!

**Implementation:**

```python
import random

def select_conflict(uncovered_conflicts):
    return random.choice(uncovered_conflicts)
```

**When it's good:** Never optimal, but useful for comparison

### Other Possible Heuristics

1. **Largest conflict first**: Opposite of smallest (rarely good)
2. **Least frequent component**: Opposite of most frequent (handle rare components first)
3. **Cost-based**: If components have costs, pick cheapest
4. **Look-ahead**: Consider what conflicts the next level will leave uncovered

### How to Think About Heuristics

**Key questions:**

1. **Does it affect correctness?** NO - All paths still explored, just in different order
2. **Does it affect completeness?** NO - All minimal solutions still found
3. **Does it affect efficiency?** YES - Different orders lead to different amounts of pruning

**Mental model:** Heuristics are like choosing which door to open first in a mansion. You'll eventually check all rooms, but a good strategy might save time.

---

## 5. Testing and Debugging

### Start with the Simplest Example

**Test case 1: Single conflict**

```python
conflict_sets = [["A", "B"]]

Expected minimal hitting sets: [["A"], ["B"]]

Why? We need to pick at least one from {A,B}.
Both A alone and B alone are minimal solutions.
```

**Test case 2: Two conflicts with overlap**

```python
conflict_sets = [["A", "B"], ["B", "C"]]

Expected minimal hitting sets: [["B"], ["A", "C"]]

Why? 
- B hits both conflicts → minimal
- A+C hits both conflicts → minimal
- A alone doesn't hit {B,C}
- C alone doesn't hit {A,B}
```

**Test case 3: Two conflicts, no overlap**

```python
conflict_sets = [["A", "B"], ["C", "D"]]

Expected minimal hitting sets: 
  [["A", "C"], ["A", "D"], ["B", "C"], ["B", "D"]]

Why? Must pick one from each conflict.
All 4 combinations are minimal.
```

### Debugging Strategy

#### Problem: Getting too many hitting sets

**Possible causes:**
1. Not filtering to minimal sets correctly
2. Including supersets

**How to debug:**

```python
# Print each hitting set and check manually
for hs in hitting_sets:
    print(f"Checking {hs}:")
    for other in hitting_sets:
        if other != hs and set(other) < set(hs):
            print(f"  ERROR: {other} is a subset of {hs}")
```

#### Problem: Missing some minimal hitting sets

**Possible causes:**
1. Pruning too aggressively
2. Not exploring all children
3. BFS queue management error

**How to debug:**

```python
# Add debug prints in tree expansion
print(f"Expanding node with path: {node.path_labels}")
print(f"  Uncovered conflicts: {uncovered}")
print(f"  Creating children for: {selected_conflict}")
```

#### Problem: Wrong results with heuristic

**How to verify:**

```python
# Compare all heuristics on same input
result_1 = run_algorithm(conflicts, heuristic="smallest")
result_2 = run_algorithm(conflicts, heuristic="most_frequent")
result_3 = run_algorithm(conflicts, heuristic="random")

# All should give SAME minimal hitting sets
assert set(map(tuple, result_1)) == set(map(tuple, result_2))
assert set(map(tuple, result_2)) == set(map(tuple, result_3))
```

### Validation Checklist

✅ **Correctness:**
- Every returned set hits all conflicts
- No returned set is a superset of another

✅ **Completeness:**
- Compare with brute-force on small examples
- Verify all expected solutions are found

✅ **Consistency:**
- Different heuristics give same minimal sets
- Running twice gives same results (unless using random)

---

## 6. Common Pitfalls

### Pitfall 1: Confusing Sets and Lists

**Problem:**

```python
hitting_set = ["A", "B", "A"]  # Oops! A appears twice
```

**Solution:** Use sets for hit checking, lists for final output

```python
# During algorithm: use sets
current_path = {"A", "B"}

# For output: convert to sorted lists
output = sorted(list(current_path))
```

### Pitfall 2: Not Checking Empty Conflict Sets

**Problem:**

```python
conflict_sets = []  # or [[]]
# Algorithm crashes or gives wrong result
```

**Solution:** Handle edge cases

```python
if not conflict_sets or all(len(cs) == 0 for cs in conflict_sets):
    return [], []  # No conflicts = no diagnoses needed
```

### Pitfall 3: Wrong Subset Check

**Problem:**

```python
# Checking if A is subset of B
if A in B:  # WRONG! This checks if A is an element of B
```

**Solution:**

```python
# Correct subset check
if set(A) <= set(B):  # A is subset of B (or equal)
if set(A) < set(B):   # A is strict subset of B (not equal)
```

### Pitfall 4: Forgetting to Prune in HS-Tree

**Problem:** Tree explodes in size, algorithm is slow

**Solution:** Always implement both pruning rules:

```python
# Rule 1: Check against known solutions
if any(known_solution <= current_path for known_solution in solutions):
    prune()

# Rule 2: Don't add component already in path
if component not in current_path:
    create_child(current_path | {component})
```

### Pitfall 5: Using DFS When You Meant BFS

**Problem:** Not finding smallest diagnoses first

**Solution:**

```python
# BFS: Use queue (FIFO)
queue = [root]
while queue:
    node = queue.pop(0)      # Take from FRONT
    # ... expand ...
    queue.extend(children)   # Add to END

# DFS: Use stack (LIFO)
stack = [root]
while stack:
    node = stack.pop()       # Take from END
    # ... expand ...
    stack.extend(children)   # Add to END
```

### Pitfall 6: Not Testing Incrementally

**Problem:** Write entire algorithm, nothing works, no idea where bug is

**Solution:** Test each function separately

```python
# Test 1: Can I check if a set hits one conflict?
assert does_hit([A, B], [B, C]) == True

# Test 2: Can I check if a set hits all conflicts?
assert hits_all([B], [[A,B], [B,C]]) == True

# Test 3: Can I generate combinations?
assert list(combinations([A,B,C], 2)) == [[A,B], [A,C], [B,C]]

# Test 4: Can I filter to minimal?
assert filter_minimal([[A], [A,B]]) == [[A]]

# Now combine them
```

---

## 7. Implementation Roadmap

### Phase 1: Brute-Force (Day 1)

1. ✅ Write `does_hit_conflict()` function
2. ✅ Write `hits_all_conflicts()` function
3. ✅ Generate combinations using `itertools.combinations`
4. ✅ Test with simple example
5. ✅ Write `filter_to_minimal()` function
6. ✅ Test with lecture example

**Time estimate:** 2-4 hours

### Phase 2: Basic HS-Tree (Day 2)

1. ✅ Design `TreeNode` class
2. ✅ Write `find_uncovered_conflicts()` function
3. ✅ Write basic BFS expansion (no heuristics yet)
4. ✅ Test on simple example
5. ✅ Compare results with brute-force

**Time estimate:** 3-5 hours

### Phase 3: Add Pruning (Day 3)

1. ✅ Implement superset pruning
2. ✅ Implement path uniqueness check
3. ✅ Test on larger examples
4. ✅ Verify pruning actually happens (count nodes)

**Time estimate:** 2-3 hours

### Phase 4: Add Heuristics (Day 4)

1. ✅ Implement smallest-conflict heuristic
2. ✅ Implement most-frequent heuristic
3. ✅ Implement random heuristic
4. ✅ Compare performance (nodes expanded, time)
5. ✅ Write comparison analysis

**Time estimate:** 2-3 hours

### Phase 5: Documentation and Testing (Day 5)

1. ✅ Test on all provided circuits
2. ✅ Write comprehensive comments
3. ✅ Update README
4. ✅ Write report

**Time estimate:** 3-4 hours

**Total:** ~15-20 hours for complete implementation

---

## 8. Key Takeaways

### Conceptual Understanding

1. **Hitting sets = picking representatives**
   - From each conflict, pick at least one guilty party

2. **Minimal = no redundancy**
   - Can't remove any component and still have a valid solution

3. **Tree search = systematic exploration**
   - BFS ensures we find small solutions first
   - Pruning avoids wasteful paths

### Implementation Wisdom

1. **Start simple, then optimize**
   - Brute-force first (verify correctness)
   - Then HS-Tree (improve efficiency)

2. **Heuristics don't change correctness**
   - They only change the order of exploration
   - All minimal solutions are still found

3. **Test incrementally**
   - Small examples first
   - Compare methods against each other
   - Verify with known examples

### For Your Report

**Discuss:**
- Why brute-force is exponential
- How pruning reduces search space
- Impact of heuristics on efficiency (measure nodes expanded)
- Trade-off between simplicity and efficiency
- When each method is appropriate

**Show:**
- Example tree for small conflict sets
- Comparison table of heuristics
- Growth of nodes expanded vs. problem size

---

## 9. Final Advice

### Do:
✅ Start with the simplest possible example  
✅ Test each function independently  
✅ Use print statements liberally during development  
✅ Compare your results with brute-force  
✅ Document as you go, not at the end  

### Don't:
❌ Try to write everything at once  
❌ Skip testing brute-force implementation  
❌ Forget edge cases (empty conflicts, single conflict)  
❌ Over-optimize before it works correctly  
❌ Assume heuristics will affect correctness  

### Remember:

> "Make it work, make it right, make it fast" - in that order!

---

## Appendix: Quick Reference

### Essential Python Tools

```python
from itertools import combinations  # Generate combinations
from collections import Counter      # Count frequencies
import random                        # Random selection

# Set operations
A & B      # Intersection
A | B      # Union
A - B      # Difference
A <= B     # A is subset of B (or equal)
A < B      # A is strict subset of B
```

### Testing Template

```python
def test_hitting_sets():
    # Lecture example
    conflicts = [["A", "B"], ["B", "C"]]
    expected = [["B"], ["A", "C"]]
    
    result = run_hitting_set_algorithm(conflicts)
    assert set(map(tuple, result)) == set(map(tuple, expected))
    
    print("✓ Test passed!")

test_hitting_sets()
```

### Debug Print Template

```python
def debug_node(node, uncovered, selected):
    print(f"Node: {node.path_labels}")
    print(f"  Uncovered: {uncovered}")
    print(f"  Selected: {selected}")
    print(f"  Creating {len(selected)} children")
```

---

**Good luck with your implementation! 🚀**

Remember: Understanding the thought process is more valuable than having perfect code. Take your time, think through each step, and don't hesitate to experiment!

