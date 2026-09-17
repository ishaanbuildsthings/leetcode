# https://leetcode.com/problems/reverse-pairs/description/
# difficulty: hard
# tags: avl tree, segment tree, merge sort tree

# Problem
# Given an integer array nums, return the number of reverse pairs in the array.

# A reverse pair is a pair (i, j) where:

# 0 <= i < j < nums.length and
# nums[i] > 2 * nums[j].

# Solution 1
# We can iterate, populate a sorted list, and binary search on it, which is O(n log n) time and O(n) space.
# Solution 2, we can also use a merge sort segment tree (I did this for practice). We store sorted lists, and for each range within a query on indices range, we do a binary search for the amount of numbers of that size. I have shown in my segment tree notes how doing a binary search on up to logN nodes simplifies to log^2n time per query, so n*log^2n total time.

class SegTree:
    def __init__(self, data):
        self.data = data
        self.n = len(data)
        self.tree = [None] * 4 * self.n
        self._buildRecurse(1, 0, self.n - 1)

    def _buildRecurse(self, i, tl, tr):
        # base case
        if tl == tr:
            self.tree[i] = [self.data[tl]]
            return

        tm = (tr + tl) // 2
        self._buildRecurse(2*i, tl, tm)
        self._buildRecurse(2*i + 1, tm + 1, tr)

        self.tree[i] = self._merge(self.tree[2*i], self.tree[2*i + 1])

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

    def _queryRecurse(self, i, tl, tr, l, r, lowerValBound, upperValBound):
        # if we have no intersection on the numbers return an identity value
        if tl > r or tr < l:
            return 0

        # if we are fully contained
        if tl >= l and tr <= r:
            bucket = self.tree[i]
            return bisect.bisect_right(bucket, upperValBound) - bisect.bisect_left(bucket, lowerValBound)

        tm = (tr + tl) // 2
        return self._queryRecurse(2*i, tl, tm, l, r, lowerValBound, upperValBound) + self._queryRecurse(2*i + 1, tm + 1, tr, l, r, lowerValBound, upperValBound)

    def query(self, l, r, lowerBound, upperBound):
        return self._queryRecurse(1, 0, self.n - 1, l, r, lowerBound, upperBound)


class Solution:
    def reversePairs(self, nums: List[int]) -> int:
        seg = SegTree(nums)
        res = 0
        for i in range(len(nums)):
            leftIndex = 0
            rightIndex = i - 1
            lowerBound = nums[i] * 2 + 1
            upperBound = 2**31 - 1
            res += seg.query(leftIndex, rightIndex, lowerBound, upperBound)
        return res