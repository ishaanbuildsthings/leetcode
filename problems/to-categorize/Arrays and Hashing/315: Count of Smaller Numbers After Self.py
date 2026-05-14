# https://leetcode.com/problems/count-of-smaller-numbers-after-self/description/
# difficulty: hard
# tags: segment tree, coordinate compression, binary search, merge sort tree, fractional cascading

# Problem
# Given an integer array nums, return an integer array counts where counts[i] is the number of smaller elements to the right of nums[i].

# Solution
# There are many ways to solve this:
# 1 - a merge sort tree. We build a segment tree on indices, each ST node holds a sorted list of elements. We can do binary search operations on each ST node to find the number of elements in a certain range that are smaller than a certain number. Normally, each query takes log^2 n time (and overall build is n log n), but with fractional cascading, we could make queries take log n time. I have implemented the non fractional cascading below.
# 2 - a segment tree built on values. The range of values is small (even if they were big we could coordinate compress), we can build a segment tree on values, and each ST holds a sorted list of indices, then we can query the values and search for appropriate indices. We have at most 2*10^4 values (call this m, less than n), so we do n queries but now each query takes log^2m time. I think again with fractional cascading we can reach n*logM time.
# 3 - A segment tree built on values with coordinate compression. In the worst case, we have m unique values, but if there are overlaps, we can use coordinate compression, making our segment tree even smaller.
# 4 - A clever segment tree where we intialize everything to 0, do a point update, then do a range sum update. This is n log n, so technically the n log M fractional cascading method could be faster.
# 5 - A clever segment tree built on values, where we do a point update for a value, then a query for the value range, this is n log M time and is simple.
# 6 - The easiest way to do it, just use a rolling sorted list from the right (can do left also, but worse), which is n log n.

class SegTree:
  def __init__(self, data):
    self.n = len(data)
    self.data = data
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

  # returns the number of elements smaller
  def _queryRecurse(self, i, tl, tr, l, r, upperBound):
    # no intersection
    if tl > r or tr < l:
      return 0

    # fully contained
    if tl >= l and tr <= r:
      countLTE = bisect.bisect_right(self.tree[i], upperBound)
      return countLTE

    tm = (tr + tl) // 2
    leftCount = self._queryRecurse(2*i, tl, tm, l, r, upperBound)
    rightCount = self._queryRecurse(2*i + 1, tm + 1, tr, l, r, upperBound)
    return leftCount + rightCount

  def querySmallerInRange(self, l, r, upperBound):
    return self._queryRecurse(1, 0, self.n - 1, l, r, upperBound)

class Solution:
    def countSmaller(self, nums: List[int]) -> List[int]:
      seg = SegTree(nums)
      res = []
      for i in range(len(nums)):
        res.append(seg.querySmallerInRange(i + 1, len(nums) - 1, nums[i] - 1))
      return res