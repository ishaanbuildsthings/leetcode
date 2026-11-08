# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bubble-sort/MinSwapsToPalindrome.py

# Minimum adjacent swaps to turn sequence into a palindrome, or -1 if no rearrangement of it is one (more than one
# value with an odd count)
# sequence: a list or a string of hashable values: negatives, floats, chars, tuples ok (not lists of lists)
def minAdjacentSwapsToPalindrome(sequence):
    n = len(sequence)
    where = {}
    for i, c in enumerate(sequence):
        where.setdefault(c, []).append(i)
    if sum(len(p) & 1 for p in where.values()) > 1:
        return -1

    dest = [-1] * n
    left, right = 0, n - 1
    for i, c in enumerate(sequence):
        if dest[i] != -1:
            continue
        j = where[c].pop()
        if j == i:
            dest[i] = n // 2
            continue
        dest[i], dest[j] = left, right
        left += 1
        right -= 1

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
