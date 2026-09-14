# TEMPLATE BY https://github.com/agrawalishaan

# O(n log n) build

# O(root n * log n) for:
# range add
# range chmin
# range chmax
# range sum
# range assign
# range count values in value range a...b

# O(1) point get

# Technically, we can get O(n * root(n * log n)) for the range operations by making _refreshSortedBlockAndPfSum take rootN time
# normally we update some values in self.valsBeforeTags (unsorted space) directly, then refresh the block
# instead, we will modify sortedBeforeTag to store (value, indexInUnSortedSpace) instead of just values
# now when we want to update some positions in self.valsBeforeTags and then call refresh, instead we loop over sorted space
# any index (which we now have access to from the tuple) that is getting updated goes into one bucket, otherwise it goes into another bucket
# each of these two buckets have a sorted value range since it came from a sorted array
# for the bucket that gets updated, we apply our update operations, whether assign, add, chmin, chmax, it will stay sorted
# now we merge the two sorted lists back in O(rootN)

from bisect import bisect_left, bisect_right
from math import isqrt, ceil

INF = float('inf')

class SqrtBlocks:
    # O(N log N)
    def __init__(self, arr):
        self.n = len(arr)
        self.blockSize = max(1, isqrt(self.n))
        self.numBlocks = ceil(self.n / self.blockSize)
        nb = self.numBlocks
        self.valsBeforeTags = arr[:]
        # every block will hold a list of its sorted values
        self.sortedBeforeTags = [None] * nb
        # every block holds a prefix sum of its sorted values
        self.pfSum = [None] * nb
        # pending add
        self.lazyAdd = [0] * nb
        self.lazyChmin = [INF] * nb
        self.lazyChmax = [-INF] * nb
        for b in range(nb):
            # rootN calls to a rootN * logN operation = N log N
            self._refreshSortedBlockAndPfSum(b)

    # O(Root(N) * log(N))
    # Re-sort one block and refresh its prefix sums. Call after editing valsBeforeTags slots directly.
    def _refreshSortedBlockAndPfSum(self, b):
        B = self.blockSize
        srt = sorted(self.valsBeforeTags[b * B:min((b + 1) * B, self.n)])
        self.sortedBeforeTags[b] = srt
        pf = []
        curr = 0
        for v in srt:
            curr += v
            pf.append(curr)
        self.pfSum[b] = pf
    
    # O(Root(N))
    # update both valsBeforeTags and sortedBeforeTags (and pfSum) to now have lazies applied
    # we can update each of those separately and safely, instead of updating valsBeforeTags and re-sorting
    # since if we apply tags to a sorted list, it stays sorted
    def _pushLaziesAndClearLazies(self, b):
        add, chmin, chmax = self.lazyAdd[b], self.lazyChmin[b], self.lazyChmax[b]
        # not required, prune
        if add == 0 and chmin == INF and chmax == -INF:
            return
        l = b * self.blockSize
        r = min(l + self.blockSize - 1, self.n - 1)
        for i in range(l, r + 1):
            self.valsBeforeTags[i] = self._valAfterTags(self.valsBeforeTags[i], add, chmin, chmax)
        curr = 0
        srt = self.sortedBeforeTags[b]
        pf = self.pfSum[b]
        for i, v in enumerate(srt):
            nval = self._valAfterTags(srt[i], add, chmin, chmax)
            srt[i] = nval
            curr += nval
            pf[i] = curr
        self.lazyAdd[b] = 0
        self.lazyChmin[b] = INF
        self.lazyChmax[b] = -INF

    # O(1) helper
    # used in both valsBeforeTags list and sortedBeforeTags
    def _valAfterTags(self, valBeforeTags, lazyAdd, lazyChmin, lazyChmax):
        nval = valBeforeTags + lazyAdd
        return self._clamp(nval, lazyChmin, lazyChmax)
    
    # O(1)
    def _clamp(self, val, chmin, chmax):
        if val < chmax:
            return chmax
        if val > chmin:
            return chmin
        return val
    
    # O(1)
    def pointGet(self, i):
        b = i // self.blockSize
        add, chmin, chmax = self.lazyAdd[b], self.lazyChmin[b], self.lazyChmax[b]
        valBeforeTag = self.valsBeforeTags[i]
        nval = valBeforeTag + add
        return self._clamp(nval, chmin, chmax)


    # O(Root(N) * logN)
    def pointAssign(self, i, newVal):
        b = i // self.blockSize
        self._pushLaziesAndClearLazies(b)
        self.valsBeforeTags[i] = newVal
        self._refreshSortedBlockAndPfSum(b) # rootN * logN
    
    # O(root(N) * logN)
    # instead of manually writing chmin, chmax, assign, and add
    # define a function which tells us how to update lazyTags, and also how to update individual indices for the partials
    def _rangeApply(self, l, r, tagOp, indexOp):
        if l > r:
            return
        B = self.blockSize
        bl, br = l // B, r // B
        vals = self.valsBeforeTags
        if bl == br:
            self._pushLaziesAndClearLazies(bl)
            for i in range(l, r + 1):
                vals[i] = indexOp(vals[i])
            self._refreshSortedBlockAndPfSum(bl) # rootN*logN
            return
        
        # left partial
        self._pushLaziesAndClearLazies(bl)
        for i in range(l, bl * B + B):
            vals[i] = indexOp(vals[i])
        self._refreshSortedBlockAndPfSum(bl) # rootN * logN

        # full blocks
        for b in range(bl + 1, br):
            tagOp(b)
            
        # right partial
        self._pushLaziesAndClearLazies(br)
        for i in range(br * B, r + 1):
            vals[i] = indexOp(vals[i])

        self._refreshSortedBlockAndPfSum(br) # rootN * logN


    # O(Root(N) * logN)
    # apply chmin to l...r
    def rangeChmin(self, l, r, x):
        def indexOp(val):
            return min(val, x)
        def tagOp(b):
            self.lazyChmin[b] = min(self.lazyChmin[b], x) # drop the ceiling
            if self.lazyChmax[b] > x: # and also drop the floor, if the ceiling dropped below the floor (now all values would be equal to x)
                self.lazyChmax[b] = x
        self._rangeApply(l, r, tagOp, indexOp)

    # O(Root(N) * logN)
    # apply chmax to l...r
    def rangeChmax(self, l, r, x):
        def indexOp(val):
            return max(val, x)
        def tagOp(b):
            self.lazyChmax[b] = max(self.lazyChmax[b], x) # raise the floor
            if self.lazyChmin[b] < x: # and also raise the ceiling, if the floor rose above the ceiling (now all values would be equal to x)
                self.lazyChmin[b] = x
        self._rangeApply(l, r, tagOp, indexOp)
    
    # O(Root(N) * logN)
    # make l...r all equal to x
    def rangeAssign(self, l, r, x):
        def indexOp(val):
            return x
        def tagOp(b):
            self.lazyAdd[b] = 0
            self.lazyChmax[b] = x
            self.lazyChmin[b] = x
        self._rangeApply(l, r, tagOp, indexOp)
    
    # O(Root(N) * logN)
    # add diff to all values in l...r
    def rangeAdd(self, l, r, diff):
        def indexOp(val):
            return val + diff
        # we had a pending add before and then a chmin/chmax, to add a new add after we can do this
        # I have an add and then a clamp. So I have a value in some range and I wanna add again. That'll put my value in some new range. So I guess I could say CH min CH max is updated.
        def tagOp(b):
            self.lazyAdd[b] += diff
            self.lazyChmax[b] += diff
            self.lazyChmin[b] += diff
        self._rangeApply(l, r, tagOp, indexOp)
    
    # O(Root(N) * logN)
    # count of values in range l...r and value range low...high
    def countValsInRange(self, l, r, low, high):
        if l > r:
            return 0
        B = self.blockSize
        bl, br = l // B, r // B
        res = 0

        if bl == br:
            for i in range(l, r + 1):
                if low <= self.pointGet(i) <= high:
                    res += 1
            return res

        # left partial
        for i in range(l, bl * B + B):
            if low <= self.pointGet(i) <= high:
                res += 1
        # right partial
        for i in range(br * B, r + 1):
            if low <= self.pointGet(i) <= high:
                res += 1
        # full blocks
        for b in range(bl + 1, br):
            add, chmin, chmax = self.lazyAdd[b], self.lazyChmin[b], self.lazyChmax[b]
            srt = self.sortedBeforeTags[b]
            sz = len(srt)
            # we want to see how many values the floor actually affects (value is < floor)
            numValsLtFloor = 0 if chmax == -INF else bisect_left(srt, chmax - add)
            # and how many the ceiling affected
            numValsGtCeil = 0 if chmin == INF else sz - bisect_right(srt, chmin - add)
            numNotAffected = sz - numValsLtFloor - numValsGtCeil
            # every value the floor touched now reads exactly chmax, so one comparison settles all of them
            if low <= chmax <= high:
                res += numValsLtFloor
            # same for the ceiling
            if low <= chmin <= high:
                res += numValsGtCeil
            # the untouched middle reads stored + add, so pull the value window back into stored space
            if numNotAffected:
                L = numValsLtFloor
                R = L + numNotAffected - 1
                res += bisect_right(srt, high - add, L, R + 1) - bisect_left(srt, low - add, L, R + 1)

        return res
    
    # O(Root(N) * logN)
    # gets sum of l...r
    def rangeSum(self, l, r):
        if l > r:
            return 0
        B = self.blockSize
        bl, br = l // B, r // B
        vals = self.valsBeforeTags
        res = 0

        if bl == br:
            for i in range(l, r + 1):
                res += self.pointGet(i)
            return res
        
        # left partial
        for i in range(l, bl * B + B):
            res += self.pointGet(i)
        # right partial
        for i in range(br * B, r + 1):
            res += self.pointGet(i)
        # full blocks
        for b in range(bl + 1, br):
            add, chmin, chmax = self.lazyAdd[b], self.lazyChmin[b], self.lazyChmax[b]
            srt = self.sortedBeforeTags[b]
            pf = self.pfSum[b]
            sz = len(srt)
            # we want to see how many values the floor actually affects (value is < floor)
            numValsLtFloor = 0 if chmax == -INF else bisect_left(srt, chmax - add)
            # and how many the ceiling affected
            numValsGtCeil = 0 if chmin == INF else sz - bisect_right(srt, chmin - add)
            numNotAffected = sz - numValsLtFloor - numValsGtCeil
            if numValsLtFloor:
                res += numValsLtFloor * chmax
            if numValsGtCeil:
                res += numValsGtCeil * chmin
            if numNotAffected:
                L = numValsLtFloor
                R = L + numNotAffected - 1
                tot = pf[R] - (pf[L - 1] if L else 0)
                tot += add * numNotAffected
                res += tot
        
        return res
        