import sys
input = sys.stdin.readline

n, m = map(int, input().split())
arr = list(map(int, input().split()))

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
    self.tree = [None] * (2 * self.n)

    # build leaves
    for i in range(self.n):
      self.tree[self.n + i] = (self.arr[i], 1) # holds min, count

    # build internal nodes
    for i in range(self.n - 1, 0, -1):
      leftMin, leftCount = self.tree[2*i]
      rightMin, rightCount = self.tree[2*i + 1]
      if leftMin < rightMin:
        self.tree[i] = (leftMin, leftCount)
      elif leftMin > rightMin:
        self.tree[i] = (rightMin, rightCount)
      else:
        self.tree[i] = (leftMin, leftCount + rightCount)

  # O(logN) update time
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = (newVal, 1)

    pos //= 2
    while pos:
      leftMin, leftCount = self.tree[2*pos]
      rightMin, rightCount = self.tree[2*pos + 1]
      if leftMin < rightMin:
        self.tree[pos] = (leftMin, leftCount)
      elif leftMin > rightMin:
        self.tree[pos] = (rightMin, rightCount)
      else:
        self.tree[pos] = (leftMin, leftCount + rightCount)
      pos //= 2

  # O(1) time
  def pointQuery(self, index):
    return self.tree[self.n + index]

  # O(logN) time
  def queryMin(self, l, r):
    res = (float("inf"), 0)
    l += self.n
    r += self.n

    while l <= r:
      if (l & 1) == 1:
        leftMin, leftCount = self.tree[l]
        if leftMin < res[0]:
          res = (leftMin, leftCount)
        elif leftMin == res[0]:
          res = (leftMin, res[1] + leftCount)
        l += 1
      if (r & 1) == 0:
        rightMin, rightCount = self.tree[r]
        if rightMin < res[0]:
          res = (rightMin, rightCount)
        elif rightMin == res[0]:
          res = (rightMin, res[1] + rightCount)
        r -= 1
      l //= 2
      r //= 2

    return res

st = PointAssignRangeMin(arr)
for _ in range(m):
    query = list(map(int, input().split()))
    if query[0] == 1:
      st.pointAssign(query[1], query[2])
    else:
      small, ct = st.queryMin(query[1], query[2] - 1)
      print(small, ct)