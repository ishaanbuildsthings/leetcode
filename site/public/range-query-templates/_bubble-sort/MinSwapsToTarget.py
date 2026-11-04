# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToTarget.py

# Minimum adjacent swaps to turn arr into target, or -1 if target isn't a rearrangement of arr
# The k-th copy of a value in arr always goes to the k-th copy of it in target (crossing two equal values never helps),
# so the answer is the number of inversions of where each element has to go
# arr / target: lists (or strings) of anything comparable
# Time: O(n log n), Space: O(n)
def minAdjacentSwapsToTarget(arr, target):
    n = len(arr)
    if len(target) != n:
        return -1

    # pair the k-th copy of each value in arr with its k-th copy in target: both sorted by (value, position)
    fromOrder = sorted(range(n), key=lambda i: arr[i])
    toOrder = sorted(range(n), key=lambda i: target[i])
    dest = [0] * n  # dest[i]: the index arr[i] has to end up at
    for i, j in zip(fromOrder, toOrder):
        if arr[i] != target[j]:
            return -1
        dest[i] = j

    # inversions of dest (pairs i < j with dest[i] > dest[j]), with a Fenwick tree over destinations
    tree = [0] * (n + 1)
    swaps = 0
    for i in range(n - 1, -1, -1):  # right to left: destinations already seen that are smaller than this one
        idx = dest[i]
        while idx > 0:
            swaps += tree[idx]
            idx -= idx & -idx
        idx = dest[i] + 1
        while idx <= n:
            tree[idx] += 1
            idx += idx & -idx

    return swaps
