# TEMPLATE BY https://github.com/agrawalishaan

# ========================
# COMPLEXITIES

# O(n log n) build

# O(root n * log n) for:
# range add
# range chmin
# range chmax
# range sum
# range assign
# range count values in value range a...b

# O(1) point get

# ========================
# Improve TC from O(rootN*logN) to O(root(N log N)), these notes reference the SqrtBlocks_CLEAN_CODE implementation at the bottom for guidance.

# Technically, we can get O(n * root(n * log n)) for the range operations by making _refreshSortedBlockAndPfSum take rootN time
# normally we update some values in self.valsBeforeTags (unsorted space) directly, then refresh the block
# instead, we will modify sortedBeforeTag to store (value, indexInUnSortedSpace) instead of just values
# now when we want to update some positions in self.valsBeforeTags and then call refresh, instead we loop over sorted space
# any index (which we now have access to from the tuple) that is getting updated goes into one bucket, otherwise it goes into another bucket
# each of these two buckets have a sorted value range since it came from a sorted array
# for the bucket that gets updated, we apply our update operations, whether assign, add, chmin, chmax, it will stay sorted
# now we merge the two sorted lists back in O(rootN)

from bisect import bisect_left, bisect_right, insort
from math import isqrt

INF = float('inf')

class SqrtBlocks_PERFORMANT:
    # O(N log N)
    def __init__(self, arr):
        self.n = n = len(arr)
        self.blockSize = B = max(1, isqrt(n))
        self.numBlocks = nb = (n + B - 1) // B
        self.valsBeforeTags = list(arr)
        self.sortedBeforeTags = [sorted(self.valsBeforeTags[b * B:min((b + 1) * B, n)]) for b in range(nb)]
        self.blockEnd = [min((b + 1) * B, n) - 1 for b in range(nb)]
        self.blockSz = [len(x) for x in self.sortedBeforeTags]
        self.pfSum = [None] * nb
        self.sumReady = False # prefix sums cost O(root N) per rebuild; don't pay until rangeSum is used
        self.lazyAdd = [0] * nb
        self.lazyChmin = [INF] * nb  # the ceiling
        self.lazyChmax = [-INF] * nb # the floor

    def _buildPf(self, b):
        run = 0
        pf = []
        for v in self.sortedBeforeTags[b]:
            run += v
            pf.append(run)
        self.pfSum[b] = pf

    # O(root N log N) -- re-sort one block after its slots were edited directly
    def _refresh(self, b):
        self.sortedBeforeTags[b] = sorted(self.valsBeforeTags[b * self.blockSize:self.blockEnd[b] + 1])
        if self.sumReady:
            self._buildPf(b)

    # O(root N) -- bake the tags in and clear them. Branches on which tags are live:
    # a ceiling-only block clamps its sorted copy with one bisect plus a slice assignment.
    def _push(self, b):
        add = self.lazyAdd[b]
        chmin = self.lazyChmin[b]
        chmax = self.lazyChmax[b]
        if add == 0 and chmin == INF and chmax == -INF:
            return
        vals = self.valsBeforeTags
        lo = b * self.blockSize
        hi = self.blockEnd[b]
        srt = self.sortedBeforeTags[b]
        sz = len(srt)
        if chmin == chmax: # assigned block
            for i in range(lo, hi + 1):
                vals[i] = chmin
            srt[:] = [chmin] * sz
        elif add == 0 and chmax == -INF: # ceiling only
            for i in range(lo, hi + 1):
                if vals[i] > chmin: vals[i] = chmin
            cut = bisect_right(srt, chmin)
            if cut < sz: srt[cut:] = [chmin] * (sz - cut)
        elif add == 0 and chmin == INF: # floor only
            for i in range(lo, hi + 1):
                if vals[i] < chmax: vals[i] = chmax
            cut = bisect_left(srt, chmax)
            if cut: srt[:cut] = [chmax] * cut
        elif chmin == INF and chmax == -INF: # add only
            for i in range(lo, hi + 1):
                vals[i] += add
            for k in range(sz):
                srt[k] += add
        else:
            for i in range(lo, hi + 1):
                v = vals[i] + add
                if v < chmax: v = chmax
                elif v > chmin: v = chmin
                vals[i] = v
            for k in range(sz):
                v = srt[k] + add
                if v < chmax: v = chmax
                elif v > chmin: v = chmin
                srt[k] = v
        if self.sumReady:
            self._buildPf(b)
        self.lazyAdd[b] = 0
        self.lazyChmin[b] = INF
        self.lazyChmax[b] = -INF

    ################ PUBLIC METHODS START HERE ################

    # O(1)
    def pointGet(self, i):
        b = i // self.blockSize
        v = self.valsBeforeTags[i] + self.lazyAdd[b]
        cx = self.lazyChmax[b]
        if v < cx: return cx
        cn = self.lazyChmin[b]
        if v > cn: return cn
        return v

    # O(root N) -- one element moves in the sorted copy, so pop + insort, no re-sort
    def pointAssign(self, i, newVal):
        b = i // self.blockSize
        self._push(b)
        vals = self.valsBeforeTags
        oldVal = vals[i]
        if oldVal == newVal:
            return
        vals[i] = newVal
        srt = self.sortedBeforeTags[b]
        srt.pop(bisect_left(srt, oldVal))
        insort(srt, newVal)
        if self.sumReady:
            self._buildPf(b)

    # O(root N log N) -- every slot in l...r becomes min(value, x)
    # A block fully covered by the range takes the O(1) tag path even when it is the
    # first or last block -- ranges anchored at 0 or n-1 are common.
    def rangeChmin(self, l, r, x):
        if l > r: return
        B = self.blockSize
        vals = self.valsBeforeTags
        blockEnd = self.blockEnd
        lazyChmin = self.lazyChmin
        lazyChmax = self.lazyChmax
        bl = l // B
        br = r // B
        if bl != br or l != bl * B or r != blockEnd[bl]:
            if l > bl * B:
                self._push(bl)
                end = blockEnd[bl] if bl != br else r
                for i in range(l, end + 1):
                    if vals[i] > x: vals[i] = x
                self._refresh(bl)
                if bl == br: return
                bl += 1
            if br != bl - 1 and r < blockEnd[br] and br >= bl:
                self._push(br)
                for i in range(br * B, r + 1):
                    if vals[i] > x: vals[i] = x
                self._refresh(br)
                br -= 1
        for b in range(bl, br + 1):
            if lazyChmin[b] > x: lazyChmin[b] = x # drop the ceiling
            if lazyChmax[b] > x: lazyChmax[b] = x # and the floor, if the ceiling went below it

    # O(root N log N) -- every slot in l...r becomes max(value, x)
    def rangeChmax(self, l, r, x):
        if l > r: return
        B = self.blockSize
        vals = self.valsBeforeTags
        blockEnd = self.blockEnd
        lazyChmin = self.lazyChmin
        lazyChmax = self.lazyChmax
        bl = l // B
        br = r // B
        if bl != br or l != bl * B or r != blockEnd[bl]:
            if l > bl * B:
                self._push(bl)
                end = blockEnd[bl] if bl != br else r
                for i in range(l, end + 1):
                    if vals[i] < x: vals[i] = x
                self._refresh(bl)
                if bl == br: return
                bl += 1
            if br != bl - 1 and r < blockEnd[br] and br >= bl:
                self._push(br)
                for i in range(br * B, r + 1):
                    if vals[i] < x: vals[i] = x
                self._refresh(br)
                br -= 1
        for b in range(bl, br + 1):
            if lazyChmax[b] < x: lazyChmax[b] = x # raise the floor
            if lazyChmin[b] < x: lazyChmin[b] = x # and the ceiling, if the floor went above it

    # O(root N log N) -- every slot in l...r becomes x
    def rangeAssign(self, l, r, x):
        if l > r: return
        B = self.blockSize
        vals = self.valsBeforeTags
        blockEnd = self.blockEnd
        bl = l // B
        br = r // B
        if bl != br or l != bl * B or r != blockEnd[bl]:
            if l > bl * B:
                self._push(bl)
                end = blockEnd[bl] if bl != br else r
                for i in range(l, end + 1):
                    vals[i] = x
                self._refresh(bl)
                if bl == br: return
                bl += 1
            if br != bl - 1 and r < blockEnd[br] and br >= bl:
                self._push(br)
                for i in range(br * B, r + 1):
                    vals[i] = x
                self._refresh(br)
                br -= 1
        for b in range(bl, br + 1):
            self.lazyAdd[b] = 0
            self.lazyChmin[b] = x
            self.lazyChmax[b] = x

    # O(root N log N) -- every slot in l...r becomes value + diff
    def rangeAdd(self, l, r, diff):
        if l > r: return
        B = self.blockSize
        vals = self.valsBeforeTags
        blockEnd = self.blockEnd
        lazyAdd = self.lazyAdd
        lazyChmin = self.lazyChmin
        lazyChmax = self.lazyChmax
        bl = l // B
        br = r // B
        if bl != br or l != bl * B or r != blockEnd[bl]:
            if l > bl * B:
                self._push(bl)
                end = blockEnd[bl] if bl != br else r
                for i in range(l, end + 1):
                    vals[i] += diff
                self._refresh(bl)
                if bl == br: return
                bl += 1
            if br != bl - 1 and r < blockEnd[br] and br >= bl:
                self._push(br)
                for i in range(br * B, r + 1):
                    vals[i] += diff
                self._refresh(br)
                br -= 1
        for b in range(bl, br + 1):
            lazyAdd[b] += diff
            if lazyChmin[b] != INF: lazyChmin[b] += diff
            if lazyChmax[b] != -INF: lazyChmax[b] += diff

    # O(root N log N) -- count of slots in l...r whose value is in low...high
    def countValsInRange(self, l, r, low, high):
        if l > r: return 0
        B = self.blockSize
        vals = self.valsBeforeTags
        blockEnd = self.blockEnd
        sortedBeforeTags = self.sortedBeforeTags
        blockSz = self.blockSz
        lazyAdd = self.lazyAdd
        lazyChmin = self.lazyChmin
        lazyChmax = self.lazyChmax
        bl = l // B
        br = r // B
        res = 0
        # partial ends, scanned slot by slot
        if bl == br and (l > bl * B or r < blockEnd[bl]):
            add = lazyAdd[bl]; cn = lazyChmin[bl]; cx = lazyChmax[bl]
            if add == 0 and cn == INF and cx == -INF:
                for i in range(l, r + 1):
                    if low <= vals[i] <= high: res += 1
            else:
                for i in range(l, r + 1):
                    v = vals[i] + add
                    if v < cx: v = cx
                    elif v > cn: v = cn
                    if low <= v <= high: res += 1
            return res
        if l > bl * B:
            add = lazyAdd[bl]; cn = lazyChmin[bl]; cx = lazyChmax[bl]
            end = blockEnd[bl]
            if add == 0 and cn == INF and cx == -INF:
                for i in range(l, end + 1):
                    if low <= vals[i] <= high: res += 1
            else:
                for i in range(l, end + 1):
                    v = vals[i] + add
                    if v < cx: v = cx
                    elif v > cn: v = cn
                    if low <= v <= high: res += 1
            bl += 1
        if r < blockEnd[br]:
            add = lazyAdd[br]; cn = lazyChmin[br]; cx = lazyChmax[br]
            start = br * B
            if add == 0 and cn == INF and cx == -INF:
                for i in range(start, r + 1):
                    if low <= vals[i] <= high: res += 1
            else:
                for i in range(start, r + 1):
                    v = vals[i] + add
                    if v < cx: v = cx
                    elif v > cn: v = cn
                    if low <= v <= high: res += 1
            br -= 1
        # whole blocks, inline -- a method call per block costs more than the work
        for b in range(bl, br + 1):
            srt = sortedBeforeTags[b]
            sz = blockSz[b]
            if not sz: continue
            add = lazyAdd[b]; cn = lazyChmin[b]; cx = lazyChmax[b]
            if add == 0 and cn == INF and cx == -INF:            # untagged
                if high >= srt[sz - 1]:
                    res += sz if low <= srt[0] else sz - bisect_left(srt, low)
                elif low <= srt[0]:
                    res += bisect_right(srt, high)
                else:
                    res += bisect_right(srt, high) - bisect_left(srt, low)
                continue
            if add == 0 and cx == -INF: # ceiling only: value = min(stored, cn)
                if cn < low: continue # every value sits below the window
                if high >= cn: # the upper bound never binds
                    res += sz if low <= srt[0] else sz - bisect_left(srt, low)
                elif low <= srt[0]:  # high < cn, so the clamp never binds either
                    res += bisect_right(srt, high)
                else:
                    res += bisect_right(srt, high) - bisect_left(srt, low)
                continue
            if add == 0 and cn == INF: # floor only: value = max(stored, cx)
                if cx > high: continue # every value sits above the window
                if low <= cx: # the lower bound never binds
                    res += sz if high >= srt[sz - 1] else bisect_right(srt, high)
                elif high >= srt[sz - 1]:
                    res += sz - bisect_left(srt, low)
                else:
                    res += bisect_right(srt, high) - bisect_left(srt, low)
                continue
            if cn == cx: # assigned
                if low <= cn <= high: res += sz
                continue
            numLtFloor = 0 if cx == -INF else bisect_left(srt, cx - add)
            numGtCeil = 0 if cn == INF else sz - bisect_right(srt, cn - add)
            mid = sz - numLtFloor - numGtCeil
            if low <= cx <= high: res += numLtFloor
            if low <= cn <= high: res += numGtCeil
            if mid:
                L = numLtFloor
                R = L + mid
                res += bisect_right(srt, high - add, L, R) - bisect_left(srt, low - add, L, R)
        return res

    # O(root N log N) -- sum of l...r. assumes finite values
    def rangeSum(self, l, r):
        if l > r: return 0
        if not self.sumReady: # first call: build every block's prefix sums
            self.sumReady = True
            for b in range(self.numBlocks):
                self._buildPf(b)
        B = self.blockSize
        vals = self.valsBeforeTags
        blockEnd = self.blockEnd
        sortedBeforeTags = self.sortedBeforeTags
        pfSum = self.pfSum
        lazyAdd = self.lazyAdd
        lazyChmin = self.lazyChmin
        lazyChmax = self.lazyChmax
        bl = l // B
        br = r // B
        res = 0
        if bl == br and (l > bl * B or r < blockEnd[bl]):
            add = lazyAdd[bl]; cn = lazyChmin[bl]; cx = lazyChmax[bl]
            if add == 0 and cn == INF and cx == -INF:
                return sum(vals[l:r + 1])
            for i in range(l, r + 1):
                v = vals[i] + add
                if v < cx: v = cx
                elif v > cn: v = cn
                res += v
            return res
        if l > bl * B:
            add = lazyAdd[bl]; cn = lazyChmin[bl]; cx = lazyChmax[bl]
            end = blockEnd[bl]
            if add == 0 and cn == INF and cx == -INF:
                res += sum(vals[l:end + 1])
            else:
                for i in range(l, end + 1):
                    v = vals[i] + add
                    if v < cx: v = cx
                    elif v > cn: v = cn
                    res += v
            bl += 1
        if r < blockEnd[br]:
            add = lazyAdd[br]; cn = lazyChmin[br]; cx = lazyChmax[br]
            start = br * B
            if add == 0 and cn == INF and cx == -INF:
                res += sum(vals[start:r + 1])
            else:
                for i in range(start, r + 1):
                    v = vals[i] + add
                    if v < cx: v = cx
                    elif v > cn: v = cn
                    res += v
            br -= 1
        for b in range(bl, br + 1):
            srt = sortedBeforeTags[b]
            sz = len(srt)
            if not sz: continue
            pf = pfSum[b]
            add = lazyAdd[b]; cn = lazyChmin[b]; cx = lazyChmax[b]
            if add == 0 and cn == INF and cx == -INF:
                res += pf[sz - 1]
                continue
            if cn == cx:
                res += sz * cn
                continue
            numLtFloor = 0 if cx == -INF else bisect_left(srt, cx - add)
            numGtCeil = 0 if cn == INF else sz - bisect_right(srt, cn - add)
            mid = sz - numLtFloor - numGtCeil
            if numLtFloor: res += numLtFloor * cx
            if numGtCeil: res += numGtCeil * cn
            if mid:
                L = numLtFloor
                R = L + mid - 1
                res += pf[R] - (pf[L - 1] if L else 0) + add * mid
        return res





class Solution:
    def shadowPairs(self, nums: list[int]) -> int:
        n = len(nums)
        # -1 means not even active in the structure
        earlyIndexBeaten = [-1] * n

        sq = SqrtBlocks_PERFORMANT(earlyIndexBeaten)
        vToI = defaultdict(list)
        for i, v in enumerate(nums):
            vToI[v].append(i)
        uniq = sorted(set(nums))
        beatenPairs = 0
        for v in uniq:
            bucket = vToI[v]
            for idx in bucket:
                lt = sq.countValsInRange(0, idx - 1, 0, idx - 1) if idx else 0
                beatenPairs += lt
            for idx in bucket:
                if idx:
                    sq.rangeChmin(0, idx - 1, idx)
            for idx in bucket:
                sq.pointAssign(idx, inf)

        totalPairs = n * (n - 1) // 2

        beatenByGte = 0
        sl = SortedList()
        for v in nums:
            gte = len(sl) - sl.bisect_left(v)
            beatenByGte += gte
            sl.add(v)

        return totalPairs - beatenPairs - beatenByGte