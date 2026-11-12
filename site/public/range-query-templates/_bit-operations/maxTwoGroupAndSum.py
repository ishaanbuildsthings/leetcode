# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/maxTwoGroupAndSum.py

# max of AND(A) + AND(B) over every split of arr into two non-empty groups A and B (each value in exactly one)
# Why it works: say x = AND(A). Moving into A every other value that contains all of x's bits keeps AND(A) = x and
# leaves B smaller, so AND(B) can only grow. So some best split has A = "every value that is a supermask of x" for a
# mask x, and the answer is the best of those (or 2 * AND(all), when both groups' ANDs equal it). A count of the
# supermasks of every mask (SOS DP) gives each candidate's two ANDs bit by bit.
# B = number of bits in max(arr): 2^B masks are tried, so values up to about 2^20 fit. Values must be >= 0; needs at
# least 2 values.
# maxTwoGroupAndSum([3, 3, 4, 4]) -> 7   # {3, 3} and {4, 4}: 3 + 4
# O(B * 2^B + N)
def maxTwoGroupAndSum(arr):
    n = len(arr)
    if n < 2:
        raise ValueError(f"maxTwoGroupAndSum: needs at least 2 values, got {n}")
    for v in arr:
        if v < 0:
            raise ValueError(f"maxTwoGroupAndSum: {v} is negative")
    bits = max(arr).bit_length()
    size = 1 << bits
    sup = [0] * size  # sup[mask] = how many values contain every bit of mask
    for v in arr:
        sup[v] += 1
    for b in range(bits):
        h = 1 << b
        for m in range(size):
            if not m & h:
                sup[m] += sup[m | h]
    withBit = [sup[1 << b] for b in range(bits)]  # how many values have bit b
    allAnd = 0
    for b in range(bits):
        if withBit[b] == n:
            allAnd |= 1 << b
    best = 2 * allAnd
    for x in range(size):
        inA = sup[x]
        if inA == 0 or inA == n:
            continue
        andA = andB = 0
        for b in range(bits):
            h = 1 << b
            withInA = sup[x | h]  # values in A with bit b
            if withInA == inA:
                andA |= h
            if withBit[b] - withInA == n - inA:
                andB |= h
        if andA + andB > best:
            best = andA + andB
    return best
