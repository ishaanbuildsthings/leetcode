# @operations: pointGet rangeMode
# @data-structure-type: sqrt
# @complexities:
#   pointGet: log(N)
#   rangeMode: sqrt(N)
#   build: N*sqrt(N)
# @memory:
#   layout: sparse
#   node: blockMode[1*N] blockCnt[1*N]
#   tags: none
#   other: idx[1*N] vals[1*N] zc[1*N] comp[1*N] positions[1*N] posIdx[1*N]
#   note: built from N (index, value) points over any index range [lo, hi], every other index 0; the sqrt mode structure is over the points only; 0's frequency is the zeros of [l, r] plus the points holding 0 (zc), and it wins whenever it is at least the points' mode frequency
# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n root n) build time, O(n) memory

# O(rootN) rangeMode(l, r) -> (mode, frequency)

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
    __slots__ = ("arr", "n", "B", "numBlocks", "vals", "comp", "positions", "posIdx", "blockMode", "blockCnt")

    # O(n root n)
    def __init__(self, arr):
        self.arr = arr
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
    def rangeMode(self, l, r):
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

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right


# Range mode over any index range [lo, hi], built from (index, value) points; every other index is 0. The sqrt mode
# structure runs on the points alone; 0 appears (zeros of [l, r]) + (points holding 0) times, and is the answer
# whenever that is at least the points' own mode frequency.


class SparseStaticRangeMode:
    __slots__ = ("lo", "hi", "idx", "vals", "inner", "zc")

    # O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    def __init__(self, lo, hi, points):
        self.lo, self.hi = lo, hi
        pts = sorted(points)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        vals = self.vals or [0]  # (a dummy element when there are no points; it is never queried)
        self.inner = RangeMode(vals)
        self.zc = [0]  # zc[k] = # of the first k points holding 0
        for v in self.vals:
            self.zc.append(self.zc[-1] + (v == 0))

    # (i0, i1, zeros): the points inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    def _span(self, l, r):
        i0, i1 = bisect_left(self.idx, l), bisect_right(self.idx, r) - 1
        return i0, i1, (r - l + 1) - (i1 - i0 + 1)

    # O(sqrtN) -- (mode, frequency) of a[l..r]; ties: any one of the tied values
    def rangeMode(self, l, r):
        i0, i1, zeros = self._span(l, r)
        if i0 > i1:
            return 0, zeros
        v, f = self.inner.rangeMode(i0, i1)
        f0 = zeros + self.zc[i1 + 1] - self.zc[i0]
        return (0, f0) if f0 >= f else (v, f)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
