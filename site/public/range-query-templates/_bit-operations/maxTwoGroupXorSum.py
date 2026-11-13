# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/maxTwoGroupXORSum.py

# max of XOR(A) + XOR(B) over every split of arr into two non-empty groups A and B (each value in exactly one)
# Why it works: with T = XOR of every value, XOR(B) = XOR(A) ^ T. A bit set in T is in exactly one of the two, so it
# adds 2^bit whatever the split; a bit clear in T is in both or in neither. So clear T's bits in every value, take the
# largest XOR M of a subset of what's left (a XOR basis), and the answer is T + 2 * M.
# Values must be >= 0; needs at least 2 values.
# maxTwoGroupXORSum([1, 2, 3]) -> 6   # {1, 2} and {3}: 3 + 3
# O(N * B)
def maxTwoGroupXORSum(arr):
    if len(arr) < 2:
        raise ValueError(f"maxTwoGroupXORSum: needs at least 2 values, got {len(arr)}")
    total = 0
    for v in arr:
        if v < 0:
            raise ValueError(f"maxTwoGroupXORSum: {v} is negative")
        total ^= v
    keep = ~total
    pivots = {}  # highest set bit -> basis value
    for v in arr:
        x = v & keep
        while x:
            top = x.bit_length() - 1
            if top not in pivots:
                pivots[top] = x
                break
            x ^= pivots[top]
    best = 0
    for top in sorted(pivots, reverse=True):
        best = max(best, best ^ pivots[top])
    # (best > 0 comes from a non-empty subset that isn't every value: all of them XOR to 0 once T's bits are cleared)
    return total + 2 * best
