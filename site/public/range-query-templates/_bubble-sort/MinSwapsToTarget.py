# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bubble-sort/MinSwapsToTarget.py

# Minimum adjacent swaps to turn sequence into target, or -1 if target isn't a rearrangement of sequence
# sequence, target: lists or strings of values that compare with each other: negatives, floats, chars, tuples ok
def minAdjacentSwapsToTarget(sequence, target):
    n = len(sequence)
    if len(target) != n:
        return -1

    fromOrder = sorted(range(n), key=lambda i: sequence[i])
    toOrder = sorted(range(n), key=lambda i: target[i])
    dest = [0] * n
    for i, j in zip(fromOrder, toOrder):
        if sequence[i] != target[j]:
            return -1
        dest[i] = j

    tree = [0] * (n + 1)
    swaps = 0
    for i in range(n - 1, -1, -1):
        idx = dest[i]
        while idx > 0:
            swaps += tree[idx]
            idx -= idx & -idx
        idx = dest[i] + 1
        while idx <= n:
            tree[idx] += 1
            idx += idx & -idx

    return swaps
