# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sqrt-movable-order-stats-sums/template.py
# @operations: append appendLeft copy countGtX countGteX countInValRange countLtX countLteX countOccurrences cut eraseRange getAll insertAt kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow merge paste pointAdd pointAssign pointGet pop popLeft rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeReverse rangeRotateLeft rangeRotateRight rangeSum size smallestGtX smallestGteX split sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK trisect
# @data-structure-type: sqrt
# @complexities:
#   append: sqrt(NlogN) amortized
#   appendLeft: sqrt(NlogN) amortized
#   copy: K+sqrt(NlogN)
#   countGtX: sqrt(NlogN)
#   countGteX: sqrt(NlogN)
#   countInValRange: sqrt(NlogN)
#   countLtX: sqrt(NlogN)
#   countLteX: sqrt(NlogN)
#   countOccurrences: sqrt(NlogN)
#   cut: sqrt(NlogN) amortized
#   eraseRange: sqrt(NlogN) amortized
#   getAll: N
#   insertAt: sqrt(NlogN) amortized
#   kthLargest: sqrt(NlogN)*log(U)
#   kthSmallest: sqrt(NlogN)*log(U)
#   largestLtX: sqrt(NlogN)
#   largestLteX: sqrt(NlogN)
#   medianHigh: sqrt(NlogN)*log(U)
#   medianLow: sqrt(NlogN)*log(U)
#   merge: sqrt(NlogN) amortized
#   paste: sqrt(NlogN) amortized
#   pointAdd: sqrt(NlogN)
#   pointAssign: sqrt(NlogN)
#   pointGet: sqrt(N/logN)
#   pop: sqrt(NlogN) amortized
#   popLeft: sqrt(NlogN) amortized
#   rangeAdd: sqrt(NlogN) amortized
#   rangeAssign: sqrt(NlogN) amortized
#   rangeChmax: sqrt(NlogN) amortized
#   rangeChmin: sqrt(NlogN) amortized
#   rangeMax: sqrt(NlogN)
#   rangeMin: sqrt(NlogN)
#   rangeReverse: sqrt(NlogN) amortized
#   rangeRotateLeft: sqrt(NlogN) amortized
#   rangeRotateRight: sqrt(NlogN) amortized
#   rangeSum: sqrt(NlogN)
#   size: 1
#   smallestGtX: sqrt(NlogN)
#   smallestGteX: sqrt(NlogN)
#   split: sqrt(NlogN) amortized
#   sumAbsDiffToMedian: sqrt(NlogN)*log(U)
#   sumAbsDiffToX: sqrt(NlogN)
#   sumGtX: sqrt(NlogN)
#   sumGteX: sqrt(NlogN)
#   sumInValRange: sqrt(NlogN)
#   sumKthLargestRange: sqrt(NlogN)*log(U)
#   sumKthSmallestRange: sqrt(NlogN)*log(U)
#   sumLargestK: sqrt(NlogN)*log(U)
#   sumLtX: sqrt(NlogN)
#   sumLteX: sqrt(NlogN)
#   sumSmallestK: sqrt(NlogN)*log(U)
#   trisect: sqrt(NlogN) amortized
#   build: N*log(N)
# @memory:
#   layout: none
#   node: vals[1*N] srt[1*N] pos[1*N] pf[1*N]
#   tags: add[1*sqrt(N/logN)] floor[1*sqrt(N/logN)] ceil[1*sqrt(N/logN)] rev[1*sqrt(N/logN)]
#   other: blocks[1*sqrt(N/logN)]
#   note: blocks of about sqrt(N log N) values that move around as whole pieces; each keeps its values, a sorted copy, where each sorted value sits, and prefix sums of the sorted copy, so cutting a block needs no re-sort; U = the largest absolute value (kth binary searches on values)

# Sqrt decomposition with movable blocks, plus sums by value and range chmin / chmax: an array you can insert into
# anywhere, erase a range from, reverse, rotate, range assign / add / chmin / chmax, cut pieces out and paste them
# back in, while asking value questions about any subarray: how many values are < x, in [low, high], equal to x;
# the sum of those values; the k-th smallest, medians, the sum of the k smallest; the nearest value above / below
# x; total distance to x or to the median; sum, min, max. (Without the sums and chmin / chmax, the plain
# sqrt-movable-order-stats template is a bit faster.)
# How: every edit first cuts blocks so the range starts and ends on block edges, then acts on whole blocks with
# tags (reverse flips a flag and reverses the block order; assign / add / chmin / chmax are one pending tag
# "v -> clamp(v + add, floor, ceil)", which never changes the sorted order, so a whole block still answers with
# binary searches and its prefix sums). Neighbors whose sizes add up to at most the block size are merged back once
# there are too many blocks. Queries read partial blocks directly and binary search whole ones.
# All indices 0-based, ranges inclusive [l, r], an index always the position in the CURRENT array. Values: integers.
from bisect import bisect_left, bisect_right
from math import inf, log2


class _Block:
    # vals: stored values in block order (backwards while rev), before the tag, empty while assigned; srt: them
    # sorted; pos[k] = where srt[k] sits in vals; pf[k] = srt[0] + ... + srt[k - 1]; each value reads
    # clamp(stored + add, floor, ceil) (floor == ceil: assigned)
    __slots__ = ("vals", "srt", "pos", "pf", "sz", "add", "floor", "ceil", "rev")

    def __init__(self, vals):
        pos = sorted(range(len(vals)), key=vals.__getitem__)
        self.vals = vals
        self.srt = [vals[p] for p in pos]
        self.pos = pos
        self.buildPf()
        self.sz = len(vals)
        self.add = 0
        self.floor = -inf
        self.ceil = inf
        self.rev = False

    def buildPf(self):
        pf = [0]
        run = 0
        for v in self.srt:
            run += v
            pf.append(run)
        self.pf = pf

    def assigned(self):
        return self.floor == self.ceil

    def tagged(self, v):
        v += self.add
        return self.floor if v < self.floor else self.ceil if v > self.ceil else v

    def valueAt(self, i):  # the value at index i of the block (in its current order)
        if self.floor == self.ceil:
            return self.floor
        return self.tagged(self.vals[self.sz - 1 - i if self.rev else i])

    def settle(self):  # a block that became assigned drops its stored values (its cuts and merges are then O(1))
        if self.floor == self.ceil:
            self.add = 0
            self.vals, self.srt, self.pos, self.pf = [], [], [], [0]

    # how many values are < x / <= x. The tag is monotone: below the floor nothing is < x, above the ceiling everything
    # is, and in between "clamp(v + add) < x" is just "v + add < x"
    def cntLess(self, x):
        if x <= self.floor:
            return 0
        if x > self.ceil:
            return self.sz
        return bisect_left(self.srt, x - self.add)

    def cntLessEq(self, x):
        if x < self.floor:
            return 0
        if x >= self.ceil:
            return self.sz
        return bisect_right(self.srt, x - self.add)

    def prefixSum(self, k):  # the sum of the k smallest values
        if k <= 0:
            return 0
        if self.floor == self.ceil:
            return self.floor * k
        # lt stored values read as the floor, those from keep on read as the ceiling
        lt = 0 if self.floor == -inf else bisect_left(self.srt, self.floor - self.add)
        keep = self.sz if self.ceil == inf else bisect_right(self.srt, self.ceil - self.add)
        res = 0
        fl = min(k, lt)
        if fl:
            res += self.floor * fl
        mid = min(k, keep) - lt
        if mid > 0:
            res += self.pf[lt + mid] - self.pf[lt] + self.add * mid
        cl = k - keep
        if cl > 0:
            res += self.ceil * cl
        return res

    def push(self):  # O(blockSize) -- bake the tag and the reversal into the stored values
        sz = self.sz
        if self.floor == self.ceil:
            self.vals = [self.floor] * sz
            self.srt = [self.floor] * sz
            self.pos = list(range(sz))
            self.add, self.floor, self.ceil, self.rev = 0, -inf, inf, False
            self.buildPf()
            return
        if self.add or self.floor != -inf or self.ceil != inf:
            tagged = self.tagged
            self.vals = [tagged(v) for v in self.vals]
            self.srt = [tagged(v) for v in self.srt]  # (the tag is monotone: still sorted)
            self.add, self.floor, self.ceil = 0, -inf, inf
            self.buildPf()
        if self.rev:
            self.vals.reverse()
            self.pos = [sz - 1 - p for p in self.pos]
            self.rev = False


class SqrtSequence:
    # O(N log N) -- arr: the initial array (a list of integers; leave it out to start empty)
    def __init__(self, arr=()):
        arr = list(arr)
        self.n = len(arr)
        self.B = B = self._targetBlockSize(self.n)
        self.nAtTidy = self.n
        self.blocks = [_Block(arr[i:i + B]) for i in range(0, self.n, B)]

    @staticmethod
    def _targetBlockSize(n):
        return max(1, int(0.5 * (n * log2(n + 2)) ** 0.5))

    TIDY = 2  # tidy once there are more than TIDY * N / blockSize blocks

    # O(blockSize) -- block j keeps its first k values, a new block j + 1 gets the rest; both keep the tags (an
    # assigned block is cut in O(1)), and the sorted copy is split by position, so neither half is re-sorted
    def _cutBlock(self, j, k):
        b = self.blocks[j]
        sz = b.sz
        right = _Block.__new__(_Block)
        right.sz, b.sz = sz - k, k
        right.add, right.floor, right.ceil, right.rev = b.add, b.floor, b.ceil, b.rev
        if b.floor == b.ceil:
            right.vals, right.srt, right.pos, right.pf = [], [], [], [0]
        else:
            # stored positions [0, cutAt) vs [cutAt, sz); reversed, the high part comes first
            cutAt = sz - k if b.rev else k
            ls, lp, hs, hp = [], [], [], []
            for v, p in zip(b.srt, b.pos):
                if p < cutAt:
                    ls.append(v)
                    lp.append(p)
                else:
                    hs.append(v)
                    hp.append(p - cutAt)
            lowVals, highVals = b.vals[:cutAt], b.vals[cutAt:]
            if b.rev:
                b.vals, b.srt, b.pos = highVals, hs, hp
                right.vals, right.srt, right.pos = lowVals, ls, lp
            else:
                right.vals, right.srt, right.pos = highVals, hs, hp
                b.vals, b.srt, b.pos = lowVals, ls, lp
            b.buildPf()
            right.buildPf()
        self.blocks.insert(j + 1, right)

    # O(blockSize) -- blocks j and j + 1 become one; the sorted copies are merged, not re-sorted
    def _mergeNext(self, j):
        a, b = self.blocks[j], self.blocks[j + 1]
        if a.floor == a.ceil and b.floor == b.ceil and a.floor == b.floor:  # (same value everywhere: O(1))
            a.sz += b.sz
            del self.blocks[j + 1]
            return
        a.push()
        b.push()
        na = a.sz
        asrt, apos, bsrt = a.srt, a.pos, b.srt
        bpos = [p + na for p in b.pos]
        srt, pos = [], []
        x = y = 0
        lenA, lenB = len(asrt), len(bsrt)
        while x < lenA and y < lenB:
            if bsrt[y] < asrt[x]:
                srt.append(bsrt[y])
                pos.append(bpos[y])
                y += 1
            else:
                srt.append(asrt[x])
                pos.append(apos[x])
                x += 1
        srt += asrt[x:]
        pos += apos[x:]
        srt += bsrt[y:]
        pos += bpos[y:]
        a.vals += b.vals
        a.srt, a.pos = srt, pos
        a.sz += b.sz
        a.buildPf()
        del self.blocks[j + 1]

    # after an edit: once there are more than about 2N / blockSize blocks (or the array halved since the last tidy),
    # cut blocks past twice the block size and merge neighbors that fit in one. A tidy walks the blocks once; each
    # merge costs O(blockSize) and removes a block some edit made, so it is paid for by that edit
    def _normalize(self):
        blocks = self.blocks
        if len(blocks) <= self.TIDY * (self.n // self.B) + 8 and 2 * self.n >= self.nAtTidy:
            return
        self.B = B = self._targetBlockSize(self.n)
        self.nAtTidy = self.n
        j = 0
        while j < len(blocks):
            if blocks[j].sz > 2 * B:
                self._cutBlock(j, B)
            while j + 1 < len(blocks) and blocks[j].sz + blocks[j + 1].sz <= B:
                self._mergeNext(j)
            j += 1

    def _splitAt(self, p):  # the index of the block starting at position p (cutting one if needed); len(blocks) at n
        start = 0
        for j, b in enumerate(self.blocks):
            sz = b.sz
            if p == start:
                return j
            if p < start + sz:
                self._cutBlock(j, p - start)
                return j + 1
            start += sz
        return len(self.blocks)

    def _locate(self, i):  # the block holding index i, and i's place inside it
        start = 0
        for j, b in enumerate(self.blocks):
            sz = b.sz
            if i < start + sz:
                return j, i - start
            start += sz

    def _visit(self, l, r):  # (whole blocks inside [l, r], the values of partly covered ones)
        whole, part = [], []
        start = 0
        for b in self.blocks:
            sz = b.sz
            end = start + sz - 1
            if start > r:
                break
            if end >= l:
                if l <= start and end <= r:
                    whole.append(b)
                elif b.floor == b.ceil:
                    part += [b.floor] * (min(r, end) - max(l, start) + 1)
                else:
                    lo, hi, tagged = max(l, start) - start, min(r, end) - start, b.tagged
                    if b.rev:
                        lo, hi = sz - 1 - hi, sz - 1 - lo
                    part += [tagged(v) for v in b.vals[lo:hi + 1]]
            start = end + 1
        return whole, part

    def _check(self, op, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"{op}: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.n}")

    # O(1) -- the current length of the array
    def size(self):
        return self.n

    # O(N) -- the whole array
    def getAll(self):
        out = []
        for b in self.blocks:
            if b.floor == b.ceil:
                out += [b.floor] * b.sz
            else:
                tagged = b.tagged
                out += [tagged(v) for v in (reversed(b.vals) if b.rev else b.vals)]
        return out

    # O(sqrt(N / log N)) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        j, o = self._locate(i)
        return self.blocks[j].valueAt(o)

    # O(sqrt(N log N)) -- a[i] = v (overwrite); needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        j, o = self._locate(i)
        b = self.blocks[j]
        b.push()
        old = b.vals[o]
        if old == v:
            return
        b.vals[o] = v
        t = b.pos.index(o)
        del b.srt[t], b.pos[t]
        u = bisect_right(b.srt, v)
        b.srt.insert(u, v)
        b.pos.insert(u, o)
        b.buildPf()

    # O(sqrt(N log N)) -- a[i] += delta; needs 0 <= i < size(), else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(sqrt(N log N)) amortized -- insert v so it becomes a[i] (i == size() appends); needs 0 <= i <= size(), else
    # IndexError
    def insertAt(self, i, v):
        if not 0 <= i <= self.n:
            raise IndexError(f"insertAt: needs 0 <= i <= size(), got i = {i}, n = {self.n}")
        j = self._splitAt(i)
        self.blocks.insert(j, _Block([v]))
        self.n += 1
        self._normalize()

    # O(sqrt(N log N)) amortized -- add v to the end
    def append(self, v):
        self.insertAt(self.n, v)

    # O(sqrt(N log N)) amortized -- add v to the front (it becomes a[0])
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(sqrt(N log N)) amortized -- remove a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def eraseRange(self, l, r):
        self._check("eraseRange", l, r)
        a = self._splitAt(l)
        b = self._splitAt(r + 1)
        del self.blocks[a:b]
        self.n -= r - l + 1
        self._normalize()

    # O(sqrt(N log N)) amortized -- remove and return the last value; needs size() >= 1, else IndexError
    def pop(self):
        if self.n < 1:
            raise IndexError("pop: needs size() >= 1")
        v = self.pointGet(self.n - 1)
        self.eraseRange(self.n - 1, self.n - 1)
        return v

    # O(sqrt(N log N)) amortized -- remove and return the first value; needs size() >= 1, else IndexError
    def popLeft(self):
        if self.n < 1:
            raise IndexError("popLeft: needs size() >= 1")
        v = self.pointGet(0)
        self.eraseRange(0, 0)
        return v

    # O(sqrt(N log N)) amortized -- reverse a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeReverse(self, l, r):
        self._check("rangeReverse", l, r)
        a = self._splitAt(l)
        b = self._splitAt(r + 1)
        seg = self.blocks[a:b]
        seg.reverse()
        for blk in seg:
            blk.rev = not blk.rev
        self.blocks[a:b] = seg
        self._normalize()

    # O(sqrt(N log N)) amortized -- cyclic shift a[l..r] left by k (a[l + k] moves to l); k can be huge or negative:
    # it is taken mod the length (negative shifts right); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateLeft(self, l, r, k):
        self._check("rangeRotateLeft", l, r)
        k %= r - l + 1
        if not k:
            return
        a = self._splitAt(l)
        m = self._splitAt(l + k)
        b = self._splitAt(r + 1)
        self.blocks[a:b] = self.blocks[m:b] + self.blocks[a:m]
        self._normalize()

    # O(sqrt(N log N)) amortized -- cyclic shift a[l..r] right by k; k can be huge or negative: it is taken mod the
    # length (negative shifts left); needs 0 <= l <= r < size(), else IndexError
    def rangeRotateRight(self, l, r, k):
        self._check("rangeRotateRight", l, r)
        self.rangeRotateLeft(l, r, -k)

    def _rangeTag(self, l, r, tag):  # tag(block) on every block inside [l, r], after cutting at both ends
        a = self._splitAt(l)
        b = self._splitAt(r + 1)
        for blk in self.blocks[a:b]:
            tag(blk)
            blk.settle()
        self._normalize()

    # O(sqrt(N log N)) amortized -- a[i] = x for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, x):
        self._check("rangeAssign", l, r)

        def tag(b):
            b.add, b.floor, b.ceil = 0, x, x
        self._rangeTag(l, r, tag)

    # O(sqrt(N log N)) amortized -- a[i] += x for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeAdd(self, l, r, x):
        self._check("rangeAdd", l, r)

        def tag(b):
            if b.floor != b.ceil:
                b.add += x
            b.floor += x  # (an infinite floor / ceiling stays infinite)
            b.ceil += x
        self._rangeTag(l, r, tag)

    # O(sqrt(N log N)) amortized -- a[i] = min(a[i], x) for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeChmin(self, l, r, x):
        self._check("rangeChmin", l, r)

        def tag(b):
            b.ceil = min(b.ceil, x)    # lower the ceiling
            b.floor = min(b.floor, x)  # and the floor, if the ceiling went below it
        self._rangeTag(l, r, tag)

    # O(sqrt(N log N)) amortized -- a[i] = max(a[i], x) for i in [l, r]; needs 0 <= l <= r < size(), else IndexError
    def rangeChmax(self, l, r, x):
        self._check("rangeChmax", l, r)

        def tag(b):
            b.floor = max(b.floor, x)  # raise the floor
            b.ceil = max(b.ceil, x)    # and the ceiling, if the floor went above it
        self._rangeTag(l, r, tag)

    # O(sqrt(N log N)) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        self._check("rangeSum", l, r)
        whole, part = self._visit(l, r)
        return sum(b.prefixSum(b.sz) for b in whole) + sum(part)

    # O(sqrt(N log N)) -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        self._check("rangeMin", l, r)
        whole, part = self._visit(l, r)
        return min([b.floor if b.floor == b.ceil else b.tagged(b.srt[0]) for b in whole] + part)

    # O(sqrt(N log N)) -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        self._check("rangeMax", l, r)
        whole, part = self._visit(l, r)
        return max([b.floor if b.floor == b.ceil else b.tagged(b.srt[-1]) for b in whole] + part)

    # O(sqrt(N log N)) -- how many i in [l, r] have a[i] < x; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        self._check("countLtX", l, r)
        whole, part = self._visit(l, r)
        return sum(b.cntLess(x) for b in whole) + sum(v < x for v in part)

    # O(sqrt(N log N)) -- how many i in [l, r] have a[i] <= x; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        self._check("countLteX", l, r)
        whole, part = self._visit(l, r)
        return sum(b.cntLessEq(x) for b in whole) + sum(v <= x for v in part)

    # O(sqrt(N log N)) -- how many i in [l, r] have a[i] > x; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        self._check("countGtX", l, r)
        return r - l + 1 - self.countLteX(l, r, x)

    # O(sqrt(N log N)) -- how many i in [l, r] have a[i] >= x; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        self._check("countGteX", l, r)
        return r - l + 1 - self.countLtX(l, r, x)

    # O(sqrt(N log N)) -- how many i in [l, r] have low <= a[i] <= high (0 when high < low); needs 0 <= l <= r <
    # size(), else IndexError
    def countInValRange(self, l, r, low, high):
        self._check("countInValRange", l, r)
        if high < low:
            return 0
        whole, part = self._visit(l, r)
        return sum(b.cntLessEq(high) - b.cntLess(low) for b in whole) + sum(low <= v <= high for v in part)

    # O(sqrt(N log N)) -- how many i in [l, r] have a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        self._check("countOccurrences", l, r)
        return self.countInValRange(l, r, x, x)

    # O(sqrt(N log N)) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGteX(self, l, r, x):
        self._check("smallestGteX", l, r)
        return self._nearest(l, r, x, True, True)

    # O(sqrt(N log N)) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        self._check("smallestGtX", l, r)
        return self._nearest(l, r, x, True, False)

    # O(sqrt(N log N)) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        self._check("largestLteX", l, r)
        return self._nearest(l, r, x, False, True)

    # O(sqrt(N log N)) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        self._check("largestLtX", l, r)
        return self._nearest(l, r, x, False, False)

    # above: the smallest value above x (or equal, when orEqual); else the largest value below x (or equal)
    def _nearest(self, l, r, x, above, orEqual):
        whole, part = self._visit(l, r)
        if above:
            cands = [v for v in part if (v >= x if orEqual else v > x)]
        else:
            cands = [v for v in part if (v <= x if orEqual else v < x)]
        for b in whole:
            if b.floor == b.ceil:
                v = b.floor
                if (v >= x if orEqual else v > x) if above else (v <= x if orEqual else v < x):
                    cands.append(v)
                continue
            k = b.cntLess(x) if above == orEqual else b.cntLessEq(x)  # values before index k are below the cut
            if above and k < b.sz:
                cands.append(b.tagged(b.srt[k]))
            if not above and k:
                cands.append(b.tagged(b.srt[k - 1]))
        if not cands:
            return None
        return min(cands) if above else max(cands)

    # O(sqrt(N log N) * log(U)) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and
    # 1 <= k <= r - l + 1, else IndexError
    def kthSmallest(self, l, r, k):
        self._check("kthSmallest", l, r)
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        whole, part = self._visit(l, r)
        part.sort()
        lo = min([b.floor if b.floor == b.ceil else b.tagged(b.srt[0]) for b in whole] + part)
        hi = max([b.floor if b.floor == b.ceil else b.tagged(b.srt[-1]) for b in whole] + part)
        while lo < hi:  # the smallest value with at least k values <= it
            mid = (lo + hi) // 2
            cnt = bisect_right(part, mid)
            for b in whole:
                cnt += b.cntLessEq(mid)
            if cnt >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo

    # O(sqrt(N log N) * log(U)) -- the k-th largest of a[l..r] (k = 1 is the max); needs 0 <= l <= r < size() and
    # 1 <= k <= r - l + 1, else IndexError
    def kthLargest(self, l, r, k):
        self._check("kthLargest", l, r)
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self.kthSmallest(l, r, r - l + 2 - k)

    # O(sqrt(N log N) * log(U)) -- the lower median of a[l..r] (with an even count, the smaller of the two middle
    # values); needs 0 <= l <= r < size(), else IndexError
    def medianLow(self, l, r):
        self._check("medianLow", l, r)
        return self.kthSmallest(l, r, (r - l + 2) // 2)

    # O(sqrt(N log N) * log(U)) -- the upper median of a[l..r] (with an even count, the larger of the two middle
    # values); needs 0 <= l <= r < size(), else IndexError
    def medianHigh(self, l, r):
        self._check("medianHigh", l, r)
        return self.kthSmallest(l, r, (r - l + 1) // 2 + 1)

    # O(sqrt(N log N)) -- the sum of the values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumLtX(self, l, r, x):
        self._check("sumLtX", l, r)
        whole, part = self._visit(l, r)
        return sum(b.prefixSum(b.cntLess(x)) for b in whole) + sum(v for v in part if v < x)

    # O(sqrt(N log N)) -- the sum of the values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumLteX(self, l, r, x):
        self._check("sumLteX", l, r)
        whole, part = self._visit(l, r)
        return sum(b.prefixSum(b.cntLessEq(x)) for b in whole) + sum(v for v in part if v <= x)

    # O(sqrt(N log N)) -- the sum of the values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumGtX(self, l, r, x):
        self._check("sumGtX", l, r)
        return self.rangeSum(l, r) - self.sumLteX(l, r, x)

    # O(sqrt(N log N)) -- the sum of the values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def sumGteX(self, l, r, x):
        self._check("sumGteX", l, r)
        return self.rangeSum(l, r) - self.sumLtX(l, r, x)

    # O(sqrt(N log N)) -- the sum of the values in [low, high] in a[l..r] (0 when high < low); needs
    # 0 <= l <= r < size(), else IndexError
    def sumInValRange(self, l, r, low, high):
        self._check("sumInValRange", l, r)
        if high < low:
            return 0
        return self.sumLteX(l, r, high) - self.sumLtX(l, r, low)

    # O(sqrt(N log N) * log(U)) -- the sum of the k smallest values of a[l..r] (0 when k == 0); needs
    # 0 <= l <= r < size() and 0 <= k <= r - l + 1, else IndexError
    def sumSmallestK(self, l, r, k):
        self._check("sumSmallestK", l, r)
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        if k == 0:
            return 0
        t = self.kthSmallest(l, r, k)  # every value < t is in, and as many copies of t as are left
        return self.sumLtX(l, r, t) + t * (k - self.countLtX(l, r, t))

    # O(sqrt(N log N) * log(U)) -- the sum of the k largest values of a[l..r] (0 when k == 0); needs
    # 0 <= l <= r < size() and 0 <= k <= r - l + 1, else IndexError
    def sumLargestK(self, l, r, k):
        self._check("sumLargestK", l, r)
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self.rangeSum(l, r) - self.sumSmallestK(l, r, r - l + 1 - k)

    # O(sqrt(N log N) * log(U)) -- the sum of the i-th through j-th smallest values of a[l..r] (1-based ranks); needs
    # 0 <= l <= r < size() and 1 <= i <= j <= r - l + 1, else IndexError
    def sumKthSmallestRange(self, l, r, i, j):
        self._check("sumKthSmallestRange", l, r)
        if not 1 <= i <= j <= r - l + 1:
            raise IndexError(
                f"sumKthSmallestRange: needs 1 <= i <= j <= r - l + 1, got i = {i}, j = {j}, r - l + 1 = {r - l + 1}")
        return self.sumSmallestK(l, r, j) - self.sumSmallestK(l, r, i - 1)

    # O(sqrt(N log N) * log(U)) -- the sum of the i-th through j-th largest values of a[l..r] (1-based ranks); needs
    # 0 <= l <= r < size() and 1 <= i <= j <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, i, j):
        self._check("sumKthLargestRange", l, r)
        if not 1 <= i <= j <= r - l + 1:
            raise IndexError(
                f"sumKthLargestRange: needs 1 <= i <= j <= r - l + 1, got i = {i}, j = {j}, r - l + 1 = {r - l + 1}")
        n = r - l + 1
        return self.sumSmallestK(l, r, n - i + 1) - self.sumSmallestK(l, r, n - j)

    # O(sqrt(N log N)) -- |a[l] - x| + ... + |a[r] - x|; needs 0 <= l <= r < size(), else IndexError
    def sumAbsDiffToX(self, l, r, x):
        self._check("sumAbsDiffToX", l, r)
        below, total, cnt = self.sumLtX(l, r, x), self.rangeSum(l, r), self.countLtX(l, r, x)
        return (x * cnt - below) + (total - below - x * (r - l + 1 - cnt))

    # O(sqrt(N log N) * log(U)) -- the total distance from a[l..r] to its lower median (the smallest total distance to
    # any one value); needs 0 <= l <= r < size(), else IndexError
    def sumAbsDiffToMedian(self, l, r):
        self._check("sumAbsDiffToMedian", l, r)
        return self.sumAbsDiffToX(l, r, self.medianLow(l, r))

    @classmethod
    def _fromBlocks(cls, blocks):  # a new one made of these blocks
        s = cls()
        s.blocks = blocks
        s.n = s.nAtTidy = sum(b.sz for b in blocks)
        s.B = cls._targetBlockSize(s.n)
        s._normalize()
        return s

    # O(sqrt(N log N)) amortized -- remove a[l..r] and return it as a SqrtSequence of its own (indices from 0); needs
    # 0 <= l <= r < size(), else IndexError
    def cut(self, l, r):
        self._check("cut", l, r)
        a = self._splitAt(l)
        b = self._splitAt(r + 1)
        piece = self.blocks[a:b]
        del self.blocks[a:b]
        self.n -= r - l + 1
        self._normalize()
        return self._fromBlocks(piece)

    # O(r - l + 1 + sqrt(N log N)) -- a[l..r] (leave out l and r: the whole array, O(N)) as a SqrtSequence of its own;
    # this one is unchanged; needs 0 <= l <= r < size(), else IndexError
    def copy(self, l=None, r=None):
        if l is None and r is None:
            l, r = 0, self.n - 1
            if self.n == 0:
                return self._fromBlocks([])
        self._check("copy", l, r)
        a = self._splitAt(l)
        b = self._splitAt(r + 1)
        piece = []
        for blk in self.blocks[a:b]:
            c = _Block.__new__(_Block)
            c.vals, c.srt, c.pos, c.pf = blk.vals[:], blk.srt[:], blk.pos[:], blk.pf[:]
            c.sz, c.add, c.floor, c.ceil, c.rev = blk.sz, blk.add, blk.floor, blk.ceil, blk.rev
            piece.append(c)
        self._normalize()
        return self._fromBlocks(piece)

    # O(sqrt(N log N)) amortized -- insert all of other (any SqrtSequence, e.g. a cut piece) so it starts at a[i];
    # other is left empty; needs 0 <= i <= size(), else IndexError
    def paste(self, i, other):
        if not 0 <= i <= self.n:
            raise IndexError(f"paste: needs 0 <= i <= size(), got i = {i}, n = {self.n}")
        j = self._splitAt(i)
        self.blocks[j:j] = other.blocks
        self.n += other.n
        other.blocks, other.n = [], 0
        self._normalize()

    # O(sqrt(N log N)) amortized -- append all of other at the end; other is left empty
    def merge(self, other):
        self.paste(self.n, other)

    # O(sqrt(N log N)) amortized -- (a[0..k-1], a[k..]) as two SqrtSequences of their own; this one is left empty;
    # needs 0 <= k <= size(), else IndexError
    def split(self, k):
        if not 0 <= k <= self.n:
            raise IndexError(f"split: needs 0 <= k <= size(), got k = {k}, n = {self.n}")
        j = self._splitAt(k)
        left, right = self.blocks[:j], self.blocks[j:]
        self.blocks, self.n = [], 0
        return self._fromBlocks(left), self._fromBlocks(right)

    # O(sqrt(N log N)) amortized -- (a[0..l-1], a[l..r], a[r+1..]) as three SqrtSequences of their own; this one is
    # left empty; needs 0 <= l <= r < size(), else IndexError
    def trisect(self, l, r):
        self._check("trisect", l, r)
        a = self._splitAt(l)
        b = self._splitAt(r + 1)
        x, y, z = self.blocks[:a], self.blocks[a:b], self.blocks[b:]
        self.blocks, self.n = [], 0
        return self._fromBlocks(x), self._fromBlocks(y), self._fromBlocks(z)
