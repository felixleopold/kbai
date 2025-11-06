print("\n\n\n")

test_list = [1, 2, 3, 1, 2]
print("List with duplicates:", test_list)

test_set = set(test_list)
print("Set:", test_set)

test_set2 = {1}

print("Set2:", test_set2)

if test_set2 <= test_set:
    print(f"Set2 {test_set2} is a subset of Set {test_set}")
else:
    print(f"Set2 {test_set2} is not a subset of Set {test_set}")