# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bit-operations/maxTwoGroupANDSum.py

# max of AND(A) + AND(B) over every split of arr into two non-empty groups A and B (each value in exactly one)
# Why it works: bits that every value has land in both ANDs whatever the split, so they count twice; set them aside.
# Then no bit can be in both ANDs, so the rest of the answer is AND(A) | AND(B): go from the highest bit down and keep
# each bit if some split still has every kept bit in AND(A) or in AND(B). Each value must sit in the group whose kept
# bits it all has, so the kept bits a value is missing must all belong to the other group: merge them (union-find over
# bits). With 2 or more merged groups of bits a split always exists (put one group of bits on each side; every value
# goes opposite the bits it misses); with 1 it exists only if some value has every kept bit.
# Values must be >= 0 (any size); needs at least 2 values.
# maxTwoGroupANDSum([3, 3, 4, 4]) -> 7   # {3, 3} and {4, 4}: 3 + 4
# O(N * B), B = number of bits in max(arr)
def maxTwoGroupANDSum(arr):
    n = len(arr)
    if n < 2:
        raise ValueError(f"maxTwoGroupANDSum: needs at least 2 values, got {n}")
    common = -1
    for v in arr:
        if v < 0:
            raise ValueError(f"maxTwoGroupANDSum: {v} is negative")
        common &= v
    vals = [v & ~common for v in arr]
    bits = max(vals).bit_length()
    parent = list(range(bits))

    def find(b):
        while parent[b] != b:
            parent[b] = parent[parent[b]]
            b = parent[b]
        return b

    missing = [-1] * n  # a kept bit the value lacks (any one: they are all merged), or -1 if it has every kept bit
    kept = groups = 0
    for t in range(bits - 1, -1, -1):
        roots, full = set(), 0
        for i in range(n):
            if vals[i] >> t & 1:
                if missing[i] == -1:
                    full += 1
            elif missing[i] != -1:
                roots.add(find(missing[i]))
        newGroups = groups - len(roots) + 1  # t merges with the groups of every value that lacks it
        if newGroups >= 2 or full:
            kept |= 1 << t
            groups = newGroups
            for r in roots:
                parent[r] = t
            for i in range(n):
                if missing[i] == -1 and not vals[i] >> t & 1:
                    missing[i] = t
    return 2 * common + kept
