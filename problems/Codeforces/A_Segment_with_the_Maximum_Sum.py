# Supports range maxSubarraySum, point assignment
# Iterative tree, 2*N memory, left child = 2*i, right child = 2*i+1
# did not seem any better than a 2N or 4N recursive tree when testing on https://leetcode.com/problems/maximize-subarray-sum-after-removing-all-occurrences-of-one-element/description/

# build: O(n)
# range maxSubarraySum: O(log n)
# point assignment: O(log n)
# point query: O(1)
class PointAssignRangeMaxSubsegmentSum:
  # O(n) build time
  def __init__(self, arr):
    self.n = len(arr)
    self.arr = arr
    # Each node stores a tuple: (totalSum, biggestPrefixSum, biggestSuffixSum, biggestSumInSegment)
    self.tree = [(0, 0, 0, 0)] * (2 * self.n)

    # build leaves
    for i in range(self.n):
      value = self.arr[i]
      self.tree[self.n + i] = (value, value, value, value)

    # build internal nodes
    for i in range(self.n - 1, 0, -1):
      (leftTotal, leftPrefix, leftSuffix, leftMax) = self.tree[2 * i]
      (rightTotal, rightPrefix, rightSuffix, rightMax) = self.tree[2 * i + 1]

      combinedTotal = leftTotal + rightTotal

      if leftPrefix > leftTotal + rightPrefix:
        combinedPrefix = leftPrefix
      else:
        combinedPrefix = leftTotal + rightPrefix

      if rightSuffix > rightTotal + leftSuffix:
        combinedSuffix = rightSuffix
      else:
        combinedSuffix = rightTotal + leftSuffix

      crossSum = leftSuffix + rightPrefix

      if leftMax > rightMax:
        tempMax = leftMax
      else:
        tempMax = rightMax

      if crossSum > tempMax:
        combinedMax = crossSum
      else:
        combinedMax = tempMax

      self.tree[i] = (combinedTotal, combinedPrefix, combinedSuffix, combinedMax)

  # O(log n) update time
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = (newVal, newVal, newVal, newVal)

    pos //= 2
    while pos:
      (leftTotal, leftPrefix, leftSuffix, leftMax) = self.tree[2 * pos]
      (rightTotal, rightPrefix, rightSuffix, rightMax) = self.tree[2 * pos + 1]

      combinedTotal = leftTotal + rightTotal

      if leftPrefix > leftTotal + rightPrefix:
        combinedPrefix = leftPrefix
      else:
        combinedPrefix = leftTotal + rightPrefix

      if rightSuffix > rightTotal + leftSuffix:
        combinedSuffix = rightSuffix
      else:
        combinedSuffix = rightTotal + leftSuffix

      crossSum = leftSuffix + rightPrefix

      if leftMax > rightMax:
        tempMax = leftMax
      else:
        tempMax = rightMax

      if crossSum > tempMax:
        combinedMax = crossSum
      else:
        combinedMax = tempMax

      self.tree[pos] = (combinedTotal, combinedPrefix, combinedSuffix, combinedMax)
      pos //= 2

  # O(log n) update time
  def pointAssignAndMutateArray(self, index, val):
    # mutate original array
    self.arr[index] = val

    # update segment tree
    pos = index + self.n
    self.tree[pos] = (val, val, val, val)

    pos //= 2
    while pos:
      (leftTotal, leftPrefix, leftSuffix, leftMax) = self.tree[2 * pos]
      (rightTotal, rightPrefix, rightSuffix, rightMax) = self.tree[2 * pos + 1]

      combinedTotal = leftTotal + rightTotal

      if leftPrefix > leftTotal + rightPrefix:
        combinedPrefix = leftPrefix
      else:
        combinedPrefix = leftTotal + rightPrefix

      if rightSuffix > rightTotal + leftSuffix:
        combinedSuffix = rightSuffix
      else:
        combinedSuffix = rightTotal + leftSuffix

      crossSum = leftSuffix + rightPrefix

      if leftMax > rightMax:
        tempMax = leftMax
      else:
        tempMax = rightMax

      if crossSum > tempMax:
        combinedMax = crossSum
      else:
        combinedMax = tempMax

      self.tree[pos] = (combinedTotal, combinedPrefix, combinedSuffix, combinedMax)
      pos //= 2

  # O(1) time
  def pointQuery(self, index):
    # return the value at arr[index]
    return self.tree[self.n + index][0]

  # O(log n) time
  def queryMaxSubsegmentSum(self, l, r):
    NEG_INF = float("-inf")
    # identity tuple: (0, -inf, -inf, -inf)
    leftResult = (0, NEG_INF, NEG_INF, NEG_INF)
    rightResult = (0, NEG_INF, NEG_INF, NEG_INF)

    l += self.n
    r += self.n
    while l <= r:
      if (l & 1) == 1:
        (leftTotal, leftPrefix, leftSuffix, leftMax) = leftResult
        (nodeTotal, nodePrefix, nodeSuffix, nodeMax) = self.tree[l]

        combinedTotal = leftTotal + nodeTotal

        if leftPrefix > leftTotal + nodePrefix:
          combinedPrefix = leftPrefix
        else:
          combinedPrefix = leftTotal + nodePrefix

        if nodeSuffix > nodeTotal + leftSuffix:
          combinedSuffix = nodeSuffix
        else:
          combinedSuffix = nodeTotal + leftSuffix

        crossSum = leftSuffix + nodePrefix

        if leftMax > nodeMax:
          tempMax = leftMax
        else:
          tempMax = nodeMax

        if crossSum > tempMax:
          combinedMax = crossSum
        else:
          combinedMax = tempMax

        leftResult = (combinedTotal, combinedPrefix, combinedSuffix, combinedMax)
        l += 1

      if (r & 1) == 0:
        (nodeTotal, nodePrefix, nodeSuffix, nodeMax) = self.tree[r]
        (rightTotal, rightPrefix, rightSuffix, rightMax) = rightResult

        combinedTotal = nodeTotal + rightTotal

        if nodePrefix > nodeTotal + rightPrefix:
          combinedPrefix = nodePrefix
        else:
          combinedPrefix = nodeTotal + rightPrefix

        if rightSuffix > rightTotal + nodeSuffix:
          combinedSuffix = rightSuffix
        else:
          combinedSuffix = rightTotal + nodeSuffix

        crossSum = nodeSuffix + rightPrefix

        if nodeMax > rightMax:
          tempMax = nodeMax
        else:
          tempMax = rightMax

        if crossSum > tempMax:
          combinedMax = crossSum
        else:
          combinedMax = tempMax

        rightResult = (combinedTotal, combinedPrefix, combinedSuffix, combinedMax)
        r -= 1

      l //= 2
      r //= 2

    # finally merge leftResult and rightResult
    (leftTotal, leftPrefix, leftSuffix, leftMax) = leftResult
    (rightTotal, rightPrefix, rightSuffix, rightMax) = rightResult

    combinedTotal = leftTotal + rightTotal

    if leftPrefix > leftTotal + rightPrefix:
      combinedPrefix = leftPrefix
    else:
      combinedPrefix = leftTotal + rightPrefix

    if rightSuffix > rightTotal + leftSuffix:
      combinedSuffix = rightSuffix
    else:
      combinedSuffix = rightTotal + leftSuffix

    crossSum = leftSuffix + rightPrefix

    if leftMax > rightMax:
      tempMax = leftMax
    else:
      tempMax = rightMax

    if crossSum > tempMax:
      combinedMax = crossSum
    else:
      combinedMax = tempMax

    return combinedMax


import sys
input = sys.stdin.readline

n, m = map(int, input().split())
arr = list(map(int, input().split()))
st = PointAssignRangeMaxSubsegmentSum(arr)
print(max(0, st.queryMaxSubsegmentSum(0, len(arr) - 1)))

for _ in range(m):
    i, v = map(int, input().split())
    st.pointAssign(i, v)
    print(max(0, st.queryMaxSubsegmentSum(0, len(arr) - 1)))