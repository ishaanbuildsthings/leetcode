# Minimum adjacent swaps to sort arr into non-decreasing order (= bubble sort swap count)
# Equal values are never swapped past each other, so ties cost nothing
# Time: O(n log n), Space: O(n)
def minAdjacentSwapsToSort(arr):
    n = len(arr)

    # original indices in the order their values get placed (smallest first, ties by position)
    placeOrder = sorted(range(n), key=lambda i: (arr[i], i))

    # Fenwick tree over original indices, 1-based internally
    # every index starts as 1 (unplaced); built in O(n)
    tree = [0] * (n + 1)
    for i in range(1, n + 1):
        tree[i] += 1
        parent = i + (i & -i)
        if parent <= n:
            tree[parent] += tree[i]

    # number of unplaced indices among original indices [0, idx)
    def countBefore(idx):
        total = 0
        while idx > 0:
            total += tree[idx]
            idx -= idx & -idx
        return total

    # adds delta to original index idx (delta = -1 marks it placed)
    def add(idx, delta):
        idx += 1
        while idx <= n:
            tree[idx] += delta
            idx += idx & -idx

    swaps = 0
    for idx in placeOrder:
        swaps += countBefore(idx)  # unplaced values still in front of this one
        add(idx, -1)

    return swaps