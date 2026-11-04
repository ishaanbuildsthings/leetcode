# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToSort.py

# sequence: a list or a string of values that compare with each other: negatives, floats, chars, tuples ok
def minAdjacentSwapsToSort(sequence):
    n = len(sequence)

    placeOrder = sorted(range(n), key=lambda i: (sequence[i], i))

    tree = [0] * (n + 1)
    for i in range(1, n + 1):
        tree[i] += 1
        parent = i + (i & -i)
        if parent <= n:
            tree[parent] += tree[i]

    def countBefore(idx):
        total = 0
        while idx > 0:
            total += tree[idx]
            idx -= idx & -idx
        return total

    def add(idx, delta):
        idx += 1
        while idx <= n:
            tree[idx] += delta
            idx += idx & -idx

    swaps = 0
    for idx in placeOrder:
        swaps += countBefore(idx)
        add(idx, -1)

    return swaps