import sys
input = sys.stdin.readline

n, m = map(int, input().split())

diffArray = [0] * (n + 1)

# ~600ms for https://leetcode.com/problems/range-sum-query-mutable/
# Supports range sum, point assignment
# Iterative tree, 2*N memory, left child = 2*i, right child = 2*i+1

# build: O(n)
# range sum: O(log n)
# point assignment: O(log n)
# point query: O(1)
class PointAssignRangeSum:
  # O(n) build time
  def __init__(self, arr):
    self.n = len(arr)
    self.arr = arr
    self.tree = [0] * (2 * self.n)

    # build leaves
    for i in range(self.n):
      self.tree[self.n + i] = self.arr[i]

    # build internal nodes
    for i in range(self.n - 1, 0, -1):
      self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

  # O(logN) update time
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = newVal

    pos //= 2
    while pos:
      self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]
      pos //= 2

  # O(logN) update time
  def pointAssignAndMutateArray(self, index, val):
    # mutate original array
    self.arr[index] = val

    # update segment tree
    pos = index + self.n
    self.tree[pos] = val

    pos //= 2
    while pos:
      self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]
      pos //= 2

  # O(1) time
  def pointQuery(self, index):
    return self.tree[self.n + index]

  # O(logN) time
  def querySum(self, l, r):
    res = 0
    l += self.n
    r += self.n

    while l <= r:
      if (l & 1) == 1:
        res += self.tree[l]
        l += 1
      if (r & 1) == 0:
        res += self.tree[r]
        r -= 1
      l //= 2
      r //= 2

    return res

st = PointAssignRangeSum(diffArray)
# print(f'init diff array: {diffArray}')
for _ in range(m):
    query = list(map(int, input().split()))
    # range add v to l...r
    if query[0] == 1:
        l, r, v = query[1:]
        r -= 1
        # print(f'range add {v} to {l} to {r}')
        oldLeftVal = st.pointQuery(l)
        # print(f'old left val is {oldLeftVal}')
        newVal = oldLeftVal + v
        # print(f'new left val is {newVal}')
        st.pointAssignAndMutateArray(l, newVal)
        oldRightVal = st.pointQuery(r + 1)
        # print(f'old right val is {oldRightVal}')
        newVal = oldRightVal - v
        # print(f'new right val is {newVal}')
        st.pointAssignAndMutateArray(r + 1, newVal)
        # print(f'diff array now: {diffArray}')

    # what is at i?
    else:
      i = query[1]
      # print(f'querying at {i}')
      total = st.querySum(0, i)
      # print(f'total is {total}')
      print(total)