# Quick Start Guide: Hitting Sets in 5 Minutes

**TL;DR:** Here's everything you need to know to implement hitting sets, condensed.

---

## The Problem in One Sentence

**Find the smallest sets of components where each set has at least one component from every conflict set.**

---

## Visual Example

```
Conflicts: {{A, B}, {B, C}}

Question: Which components must be faulty?

Answer: Either {B} alone, OR both {A, C}

Why?
  {B}    hits [A,B]? YES (B is there) hits [B,C]? YES (B is there) ✓
  {A,C}  hits [A,B]? YES (A is there) hits [B,C]? YES (C is there) ✓
  {A}    hits [A,B]? YES            hits [B,C]? NO              ✗
```

---

## Method 1: Brute Force (5 Steps)

```python
# Step 1: Get all components
components = {A, B, C}

# Step 2: Try all combinations (size 1, then 2, then 3...)
for size in 1 to 3:
    for combo in combinations(components, size):
        # Step 3: Check if it hits all conflicts
        if hits_all(combo, conflicts):
            hitting_sets.append(combo)

# Step 4: Filter to minimal (remove supersets)
minimal = [hs for hs in hitting_sets 
           if no other hs is a subset of this hs]

# Step 5: Done!
return minimal
```

**Time:** O(2^n) - exponential but simple

---

## Method 2: HS-Tree (The Smart Way)

```
Build a tree:
- Each node = partial diagnosis
- Each edge = "add this component"
- Leaves = complete diagnoses

Example:
                ROOT
               /    \
              A      B
             / \      |
            C   ✗    DONE!
           /
        DONE!

Solutions: {B}, {A,C}
```

**Key ideas:**
1. **BFS** - Find small solutions first
2. **Prune** - Stop if path contains an existing solution
3. **No duplicates** - Don't add same component twice in a path

**Pseudocode:**

```python
queue = [Node(path=∅)]
solutions = []

while queue:
    node = queue.pop(0)  # BFS: take from front
    
    # Pruning
    if any(solution ⊆ node.path for solution in solutions):
        continue
    
    # Find uncovered conflicts
    uncovered = [c for c in conflicts if node.path ∩ c == ∅]
    
    if not uncovered:
        # All covered! Found a solution
        solutions.append(node.path)
    else:
        # Expand: pick one conflict and create children
        conflict = pick_one(uncovered)  # ← Heuristic goes here!
        for component in conflict:
            if component not in node.path:
                child = Node(path = node.path ∪ {component})
                queue.append(child)

return solutions
```

**Time:** Much faster with pruning! ~O(k × n^d) where d = diagnosis size

---

## Heuristics (Which Conflict to Expand?)

### Option 1: Smallest Conflict
```python
conflict = min(uncovered, key=len)
```
**Why:** Fewer branches = faster

### Option 2: Most Frequent Component
```python
freq = count_components(uncovered)
conflict = max(uncovered, key=lambda c: max(freq[x] for x in c))
```
**Why:** Pick components that appear often

### Option 3: Random
```python
conflict = random.choice(uncovered)
```
**Why:** Baseline for comparison

**Important:** All heuristics find the same solutions, just in different order!

---

## Testing: The Sacred Example

```python
conflicts = [["A", "B"], ["B", "C"]]
result = your_algorithm(conflicts)

# Must return (in any order):
expected = [["B"], ["A", "C"]]

assert set(map(tuple, result)) == set(map(tuple, expected))
```

If this works, you're probably correct!

---

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Including supersets | Too many results | Filter: remove if other ⊂ this |
| Missing solutions | Too few results | Check pruning logic |
| Duplicates | Same set twice | Use sets, not lists during algorithm |
| Wrong with heuristic | Different results | Heuristics shouldn't change results! |

---

## The Checklist

Before you submit:

- ✅ Works on `{{A,B}, {B,C}}` → `{{B}, {A,C}}`
- ✅ Brute-force and HS-tree give same results
- ✅ All heuristics give same results
- ✅ Works on all 7 provided circuits
- ✅ Code has comments
- ✅ README explains your approach

---

## One-Paragraph Explanation for Your Report

> "The hitting set algorithm finds minimal sets of components that intersect every conflict set, representing diagnoses that explain all observed faults. I implemented two approaches: (1) a brute-force method that enumerates all combinations and filters to minimal sets, providing a simple baseline; and (2) Reiter's HS-Tree algorithm using BFS with pruning, which systematically builds diagnoses while eliminating non-minimal paths. I tested three heuristics for conflict selection in the HS-Tree: smallest conflict first (minimizes branching), most frequent component (prioritizes critical components), and random selection (baseline). All methods found identical minimal hitting sets on test cases, confirming correctness, while the HS-Tree with smallest-conflict heuristic showed superior efficiency by expanding fewer nodes."

---

## Resources

- **Full implementation guide:** `IMPLEMENTATION_GUIDE.md` (detailed walkthrough)
- **README:** `README.md` (comprehensive documentation)
- **Test script:** `test_circuits.py` (validate your implementation)
- **Example code:** `hittingsets.py` (reference implementation)

---

**You've got this! 💪**

Start with brute-force, make sure it works on the simple example, then build the tree. Good luck!

