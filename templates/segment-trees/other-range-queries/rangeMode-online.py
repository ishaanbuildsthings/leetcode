# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n root n) build time, O(n) memory

# O(rootN) query(l, r) -> (mode, frequency)

# ========================
"""
How do range mode work in rootN?

First, we split the array into rootN blocks. I want to be able to answer: "what is the mode from bl...br and how many time does it occur)
This is easy, from the starting point of each block sweep to the end of the array, every time we hit the end of the block we know the mode for bl...some other block and we store the answer. We do rootN sweeps each N time.

Now I claim in a rangeMode(l, r) query, the mode is one of:
-the mode JUST inside the full blocks portion
-any one of the partial values

It wouldn't be possible for a value to be the mode if it's not a partial and not the mode of the full region.

We can find the mode of just the inside full blocks portion since we precomputed it.

Now we want to know for each partial, how many times does it occur in the full region? We could do this with NrootN memory by, for each value, computing a prefix sum of size rootN, like for each block. But we can do N memory:

Map all values -> indices, and also an index to its position in that index bucket, so [5, 2, 5] has:

5 : [0, 2]
2 : [1]

But also 0->0, 1->1, 2->1 as the global index -> inside bucket index, mapping.

Now for any partial value we can find exactly where it occurs in its indices list in O(1). We then jump ahead by modeMiddleFrequency spots and check if the ending spot is <= qr or not.
"""

# ========================


from math import isqrt


class RangeMode:
    __slots__ = ("n", "B", "numBlocks", "vals", "comp", "positions", "posIdx", "blockMode", "blockCnt")

    # O(n root n)
    def __init__(self, arr):
        self.n = n = len(arr)
        self.B = B = max(1, isqrt(n))
        self.numBlocks = numBlocks = (n + B - 1) // B

        # coordinate compress so counting can use a flat list
        self.vals = sorted(set(arr))
        idOf = {val: i for i, val in enumerate(self.vals)}
        self.comp = comp = [idOf[val] for val in arr]

        # positions[valId] = sorted indices holding valId
        # posIdx[i] = where index i sits inside positions[comp[i]]
        self.positions = positions = [[] for _ in range(len(self.vals))]
        self.posIdx = posIdx = [0] * n
        for i, valId in enumerate(comp):
            posIdx[i] = len(positions[valId])
            positions[valId].append(i)

        # blockMode[startBlock * numBlocks + endBlock] = mode (compressed id) of those blocks
        # blockCnt[...] = its frequency
        self.blockMode = blockMode = [0] * (numBlocks * numBlocks)
        self.blockCnt = blockCnt = [0] * (numBlocks * numBlocks)
        cnt = [0] * len(self.vals)
        for startBlock in range(numBlocks):
            best = 0
            bestVal = 0
            row = startBlock * numBlocks
            for endBlock in range(startBlock, numBlocks):
                for i in range(endBlock * B, min(n, (endBlock + 1) * B)):
                    valId = comp[i]
                    cnt[valId] += 1
                    if cnt[valId] > best:
                        best = cnt[valId]
                        bestVal = valId
                blockMode[row + endBlock] = bestVal
                blockCnt[row + endBlock] = best
            # reset only what we touched
            for i in range(startBlock * B, n):
                cnt[comp[i]] = 0

    #################### PUBLIC METHODS START HERE ####################

    # O(rootN) -- (mode, frequency) of arr[l...r] inclusive. requires 0 <= l <= r < n
    # ties: returns any one of the tied values
    def query(self, l, r):
        B = self.B
        comp = self.comp
        positions = self.positions
        posIdx = self.posIdx
        leftBlock = l // B
        rightBlock = r // B

        if rightBlock - leftBlock <= 1:
            # no whole middle block, every element is a candidate
            best = 0
            bestVal = comp[l]
            leftEdgeEnd = r
            rightEdgeStart = r + 1
        else:
            idx = (leftBlock + 1) * self.numBlocks + (rightBlock - 1)
            best = self.blockCnt[idx]
            bestVal = self.blockMode[idx]
            leftEdgeEnd = (leftBlock + 1) * B - 1
            rightEdgeStart = rightBlock * B

        # left edge: is the (best + 1)-th copy counting forward from here still <= r?
        for i in range(l, leftEdgeEnd + 1):
            valId = comp[i]
            plist = positions[valId]
            k = posIdx[i]
            while k + best < len(plist) and plist[k + best] <= r:
                best += 1
                bestVal = valId

        # right edge: is the (best + 1)-th copy counting backward from here still >= l?
        for i in range(rightEdgeStart, r + 1):
            valId = comp[i]
            plist = positions[valId]
            k = posIdx[i]
            while k - best >= 0 and plist[k - best] >= l:
                best += 1
                bestVal = valId

        return self.vals[bestVal], best