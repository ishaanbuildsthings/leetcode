# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToPalindrome.py

# Minimum adjacent swaps to turn s into a palindrome, or -1 if no rearrangement of s is one (more than one value with
# an odd count)
# Greedy: the leftmost unplaced element pairs with the last unplaced copy of its value, taking the outermost free pair
# of slots; the lone copy of the odd-count value (if any) goes to the middle. Every element then has a destination, and
# the answer is the number of inversions of the destinations
# s: a string, or a list of anything hashable
# Time: O(n log n), Space: O(n)
def minAdjacentSwapsToPalindrome(s):
    n = len(s)
    where = {}  # value -> its indices, left to right
    for i, c in enumerate(s):
        where.setdefault(c, []).append(i)
    if sum(len(p) & 1 for p in where.values()) > 1:
        return -1

    dest = [-1] * n  # dest[i]: the index s[i] has to end up at
    left, right = 0, n - 1
    for i, c in enumerate(s):
        if dest[i] != -1:
            continue
        j = where[c].pop()  # the last unplaced copy of c (the copies placed on the left are at the front of the list)
        if j == i:  # the lone copy of the odd-count value
            dest[i] = n // 2
            continue
        dest[i], dest[j] = left, right
        left += 1
        right -= 1

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
