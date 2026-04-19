# For the k-big indices problem: https://leetcode.com/problems/count-the-number-of-k-big-indices/
# I made a ST on the values instead of indices (no compression was needed due to small value size), and each ST node holds an array that is sorted

from sortedcontainers import SortedList

# the ST nodes are ranges of number values, so for instance all numbers < k, and each node holds a list that is sorted of the relevant indices
class SegTree:
    def __init__(self, n, arr):
        self.n = n
        self.tree = [0] * 4 * self.n
        # for the array, find all the indices of each element
        self.indices = defaultdict(list)
        for i in range(len(arr)):
            self.indices[arr[i]].append(i)
        self._buildRecurse(1, 0, self.n - 1)

    def _buildRecurse(self, i, tl, tr):
        # base case
        if tl == tr:
            self.tree[i] = [*self.indices[tl]] # unpacking not needed but probably good practice
            return

        tm = (tr + tl) // 2
        self._buildRecurse(2*i, tl, tm)
        self._buildRecurse(2*i + 1, tm + 1, tr)
        parentSortedList = self._merge(self.tree[2*i], self.tree[2*i + 1])
        self.tree[i] = parentSortedList

    # merges two sorted lists
    def _merge(self, a, b):
        newList = []
        i = 0
        j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                newList.append(a[i])
                i += 1
            else:
                newList.append(b[j])
                j += 1
        if i < len(a):
            for k in range(i, len(a)):
                newList.append(a[k])
        if j < len(b):
            for g in range(j, len(b)):
                newList.append(b[g])
        return newList

    # returns the number of indices, for a numerical bound range, in an index bound range
    def _queryRecurse(self, i, tl, tr, lowerBound, upperBound, leftIndex, rightIndex):
        # if we have no intersection
        if lowerBound > tr or upperBound < tl:
            return 0 # identity value

        # if we are fully contained
        if tl >= lowerBound and tr <= upperBound:
            sortedList = self.tree[i]
            return bisect.bisect_right(sortedList, rightIndex) - bisect.bisect_left(sortedList, leftIndex)

        tm = (tr + tl) // 2
        # otherwise we take the merging
        leftResult = self._queryRecurse(2*i, tl, tm, lowerBound, upperBound, leftIndex, rightIndex)
        rightResult = self._queryRecurse(2*i + 1, tm + 1, tr, lowerBound, upperBound, leftIndex, rightIndex)
        return leftResult + rightResult

    def query(self, lowerBound, upperBound, leftIndex, rightIndex):
        return self._queryRecurse(1, 0, self.n - 1, lowerBound, upperBound, leftIndex, rightIndex)

class Solution:
    def kBigIndices(self, nums: List[int], k: int) -> int:
        T = SegTree(max(nums) + 1, nums)
        res = 0

        for i in range(len(nums)):
            lowerBound = 0
            upperBound = nums[i] - 1
            left_leftIndex = 0
            left_rightIndex = i - 1

            leftCount = T.query(lowerBound, upperBound, left_leftIndex, left_rightIndex)

            if leftCount < k:
                continue

            right_leftIndex = i + 1
            right_rightIndex = len(nums) - 1

            rightCount = T.query(lowerBound, upperBound, right_leftIndex, right_rightIndex)

            res += leftCount >= k and rightCount >= k

        return res

