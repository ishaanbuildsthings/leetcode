import sys
input = sys.stdin.readline
 
n, m = map(int, input().split())
 
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
      leftMin, leftMinIndex = self.tree[2 * i]
      rightMin, rightMinIndex = self.tree[2 * i + 1]
      if leftMin < rightMin:
        self.tree[i] = (leftMin, leftMinIndex)
      else:
        self.tree[i] = (rightMin, rightMinIndex)
 
  # O(logN) update time
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = (newVal, index)
 
    pos //= 2
    while pos:
      leftMin, leftMinIndex = self.tree[2 * pos]
      rightMin, rightMinIndex = self.tree[2 * pos + 1]
      if leftMin < rightMin:
        self.tree[pos] = (leftMin, leftMinIndex)
      else:
        self.tree[pos] = (rightMin, rightMinIndex)
      pos //= 2
 
  # O(logN) update time
  def pointAssignAndMutateArray(self, index, val):
    # mutate original array
    self.arr[index] = (val, index)
 
    # update segment tree
    pos = index + self.n
    self.tree[pos] = (val, index)
 
    pos //= 2
    while pos:
      leftMin, leftMinIndex = self.tree[2 * pos]
      rightMin, rightMinIndex = self.tree[2 * pos + 1]
      if leftMin < rightMin:
        self.tree[pos] = (leftMin, leftMinIndex)
      else:
        self.tree[pos] = (rightMin, rightMinIndex)
      pos //= 2
 
  # O(1) time
  def pointQuery(self, index):
    return self.tree[self.n + index]
 
  # O(logN) time
  def queryMin(self, l, r):
    resMin = float("inf")
    resIndex = None
    l += self.n
    r += self.n
 
    while l <= r:
      if (l & 1) == 1:
        if self.tree[l][0] < resMin:
          resMin = self.tree[l][0]
          resIndex = self.tree[l][1]
        l += 1
      if (r & 1) == 0:
        if self.tree[r][0] < resMin:
          resMin = self.tree[r][0]
          resIndex = self.tree[r][1]
        r -= 1
      l //= 2
      r //= 2
 
    return resMin, resIndex
 
 
arr = [(10**18, i) for i in range(n)] # each node will have (height, index) since we need the index to reset it
st = PointAssignRangeMin(arr)
# print(f'init arr: {st.arr}')
 
for _ in range(m):
    query = list(map(int, input().split()))
    # print('------------')
    if query[0] == 1:
        i, h = query[1:]
        # print(f'updating {i} to {h}')
        st.pointAssignAndMutateArray(i, h)
        # print(f'arr now: {st.arr}')
    else:
      l, r, p = query[1:]
      r -= 1
      # print(f'querying from {l} to {r}, for p = {p}')
      destroyed = 0
      while True:
        smallest, idx = st.queryMin(l, r)
        # print(f'smallest: {smallest}, idx: {idx}')
        if smallest > p:
          # print(f'smallest too big, break')
          break
        st.pointAssignAndMutateArray(idx, 10**18)
        # print(f'arr now: {st.arr}')
        destroyed += 1
      print(destroyed)