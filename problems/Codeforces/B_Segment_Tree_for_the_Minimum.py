# Supports range min, point assignment
# Iterative tree, 2*N memory, left child = 2*i, right child = 2*i+1

# build: O(n)
# range min: O(log n)
# point assignment: O(log n)
# point query: O(1)
fmin = lambda x, y: x if x < y else y
class PointAssignRangeMin:
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
      self.tree[i] = fmin(self.tree[2 * i], self.tree[2 * i + 1])

  # O(logN) update time
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = newVal

    pos //= 2
    while pos:
      self.tree[pos] = fmin(self.tree[2 * pos], self.tree[2 * pos + 1])
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
      self.tree[pos] = fmin(self.tree[2 * pos], self.tree[2 * pos + 1])
      pos //= 2

  # O(1) time
  def pointQuery(self, index):
    return self.tree[self.n + index]

  # O(logN) time
  def queryMin(self, l, r):
    res = float("inf")
    l += self.n
    r += self.n

    while l <= r:
      if (l & 1) == 1:
        res = fmin(res, self.tree[l])
        l += 1
      if (r & 1) == 0:
        res = fmin(res, self.tree[r])
        r -= 1
      l //= 2
      r //= 2

    return res


import sys
input = sys.stdin.readline

n, m = map(int, input().split())
arr = list(map(int, input().split()))
st = PointAssignRangeMin(arr)

for _ in range(m):
    query = list(map(int, input().split()))
    if query[0] == 1:
      st.pointAssign(query[1], query[2])
    else:
      print(st.queryMin(query[1], query[2] - 1))