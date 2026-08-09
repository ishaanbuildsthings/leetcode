# Wrong Answer
# 728 / 999 testcases passed
# Input
# nums =
# [9,8,12,5,9,9]
# queries =
# [[2,3,16],[1,1,5]]
# Use Testcase
# Output
# [5]
# Expected
# [4]







# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Complexities:
# Build: O(n)
# Space: O(n)
# Query/Update: O(log N)

# baseFn: (val, i) => ...
# combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
# tupleNametags: If baseFn returns a tuple, we can supply nametags for each value, like ('min', 'max'), used for debugging

class SegmentTree:
    def __init__(self, arr, baseFn, combine, tupleNametags=None):
        self.n = len(arr)
        self.arr = arr
        self.tree = [None] * (4 * self.n)
        self._combine = combine
        self._baseFn = baseFn
        self.tupleNametags = tupleNametags
        self._build(1, 0, self.n - 1)

    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = self._baseFn(self.arr[tl], tl)
            return
        tm = (tr + tl) // 2
        self._build(2 * i, tl, tm)
        self._build(2 * i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

    def _queryRecurse(self, i, tl, tr, l, r):
        # print(f"Getting useful intersection from [{tl},{tr}] for query [{l},{r}]")
        if l <= tl and tr <= r:
            # print(f'Fully in bounds, returning node value:')
            # print(f'{self._getPrintFormattedVal(self.tree[i], tl, tr)}\n')
            return self.tree[i]

        tm = (tl + tr) // 2
        # print(f'left child: [{tl},{tm}], right child: [{tm + 1},{tr}]\n')

        if l > tm:
            # print(f'Left child [{tl},{tm}] would have no overlap, so only using right\n')
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        elif r < tm + 1:
            # print(f'Right child [{tm+1},{tr}] would have no overlap, so only using left\n')
            return self._queryRecurse(2 * i, tl, tm, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        combinedResult = self._combine(leftResult, rightResult)
        # print(f"Combining results for parent [{tl},{tr}] for query [{l},{r}]:\n"
        #       f"  left useful: {self._getPrintFormattedVal(leftResult, max(l, tl), min(tm, r))}\n"
        #       f"  right useful: {self._getPrintFormattedVal(rightResult, max(l, tm + 1), min(r, tr))}\n"
        #       f"  -> combined useful: {self._getPrintFormattedVal(combinedResult, max(l, tl), min(r, tr))}\n")
        return combinedResult


    def _getPrintFormattedVal(self, val, tl, tr):
        subarray = self.arr[tl:tr + 1]
        prefix = f'[{tl},{tr}] subarray: {subarray} '
        if self.tupleNametags is None:
            if isinstance(val, tuple):
                return prefix + f"({', '.join(str(v) for v in val)})"
            return prefix + str(val)
        return f'{prefix}({", ".join(f"{tag}: {v}" for tag, v in zip(self.tupleNametags, val))})'

    def _line(self):
        return '________________________________________'

    def _updateRecurse(self, i, tl, tr, posToBeUpdated):
        # print(f'descending down to update, pos to be updated: {posToBeUpdated}, current node tl={tl}, tr={tr}')
        if tl == tr:
            # print(f'reached leaf node, updating then going back up and combining')
            self.tree[i] = self._baseFn(self.arr[tl], tl)
            # print(F'updated node {tl=}, {tr=} to be: {self.tree[i]}')
            return
        tm = (tl + tr) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2 * i, tl, tm, posToBeUpdated)
        else:
            self._updateRecurse(2 * i + 1, tm + 1, tr, posToBeUpdated)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])
        # print(F'updated node {tl=}, {tr=} to be: {self.tree[i]}')


    ################ PUBLIC METHODS START HERE ################

    def updateAndMutateArray(self, index, newVal):
        # print(f'{self._line()} UPDATE CALLED, index={index}, newVal={newVal} {self._line()}')
        self.arr[index] = newVal
        self._updateRecurse(1, 0, self.n - 1, index)
        # print(f'new array: {self.arr}')

    def query(self, l, r):
        # print(f'{self._line()} QUERY CALLED, l={l} r={r} {self._line()}')
        # print(f'array: {self.arr}\n')
        queryResult = self._queryRecurse(1, 0, self.n - 1, l, r)
        # print(f'query result: {queryResult}')
        return queryResult

        
class Solution:
    def countOfPeaks(self, nums: list[int], queries: list[list[int]]) -> list[int]:
        # nums = [9, 8, 12, 5, 9, 9]
        # queries = [[2, 3, 16], [1, 1, 5]]

        # not a peak subarray if mono-increasing or mono-decreasing
        # otherwise we are a peak

        # find location of first drop and first go up, need both?


        # find the sum of increasing lengths and decreasing lengths squared with only lengths >= 3


        # number of peaks alone sufficient?

        n = len(nums)


        # each node stores
        # (tl, tr, leftmostPeak, rightmostPeak, sumSq)
        def basefn(v, i):

            if i > 0 and i < n - 1 and v > nums[i - 1] and v > nums[i + 1]:
                peak = i
            else:
                peak = None

            # print(f'base called, is peak?: {peak}')

            return (i, i, peak, peak, 1)

        def sq(x):
            return x * (x + 1) // 2

        def agg(a, b):
            atl, atr, aLeftPeak, aRightPeak, aSumSq = a
            btl, btr, bLeftPeak, bRightPeak, bSumSq = b

            if aLeftPeak is None:
                nleftPeak = bLeftPeak
            else:
                nleftPeak = aLeftPeak

            if bRightPeak is None:
                nrightPeak = aRightPeak
            else:
                nrightPeak = bRightPeak

            nSumSq = aSumSq + bSumSq

            # subtract the previous block that aRightPeak was contributing
            leftWidth = atr - atl + 1

            # this is the width we span for that block
            leftSpan = leftWidth if aRightPeak is None else (atr - aRightPeak + 1)

            leftLost = sq(leftSpan)

            rightWidth = btr - btl + 1
            rightSpan = rightWidth if bLeftPeak is None else (bLeftPeak - btl + 1)

            rightLost = sq(rightSpan)

            nSumSq -= leftLost
            nSumSq -= rightLost

            LEFT = aRightPeak if aRightPeak is not None else atl
            RIGHT = bLeftPeak if bLeftPeak is not None else btr

            WIDTH = (RIGHT - LEFT) + 1

            GAIN = sq(WIDTH)

            nSumSq += GAIN

            return (atl, btr, nleftPeak, nrightPeak, nSumSq)
        

            
        st = SegmentTree(nums, basefn, agg)

        # print(f'========================')
            
        isPeak = [False] * n
        for i in range(1, n - 1):
            if nums[i] > nums[i - 1] and nums[i] > nums[i + 1]:
                isPeak[i] = True

        def isPeakFn(i):
            if i > 0 and i < n - 1 and nums[i] > nums[i - 1] and nums[i] > nums[i + 1]:
                return True
            return False

        res = []
        for qtype, a, b in queries:
            if qtype == 1:
                node = st.query(a, b)
                width = b - a + 1
                total = sq(width)
                bad = node[-1]
                res.append(total - bad)
            else:
                st.updateAndMutateArray(a, b)
                # print(f'mutated array, now:')
                # print(nums)

                if a > 0:
                    # true state of if left is a peak
                    nowLeft = isPeakFn(a - 1)
                    before = isPeak[a - 1]

                    if nowLeft != before:
                        st.updateAndMutateArray(a - 1, nums[a - 1])

                        isPeak[a - 1] = nowLeft

                if a < n - 1:
                    nowRight = isPeakFn(a + 1)
                    before = isPeak[a + 1]
                    if nowRight != before:
                        st.updateAndMutateArray(a + 1, nums[a + 1])

                        isPeak[a + 1] = nowRight

                isPeak[a] = isPeakFn(a)
                        
                        
        return res


        


        

        
            



























        

        
        