n = int(input())
heights = list(map(int, input().split()))
beauties = list(map(int, input().split()))

fmax = lambda x, y: x if x > y else y
class PointAssignRangeMax:
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
      self.tree[i] = fmax(self.tree[2 * i], self.tree[2 * i + 1])

  # O(logN) update time
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = newVal

    pos //= 2
    while pos:
      self.tree[pos] = fmax(self.tree[2 * pos], self.tree[2 * pos + 1])
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
      self.tree[pos] = fmax(self.tree[2 * pos], self.tree[2 * pos + 1])
      pos //= 2

  # O(1) time
  def pointQuery(self, index):
    return self.tree[self.n + index]

  # O(logN) time
  def queryMax(self, l, r):
    res = float("-inf")
    l += self.n
    r += self.n

    while l <= r:
      if (l & 1) == 1:
        res = fmax(res, self.tree[l])
        l += 1
      if (r & 1) == 0:
        res = fmax(res, self.tree[r])
        r -= 1
      l //= 2
      r //= 2

    return res

dp = [0] * (len(heights)+1) # dp[height] tells us the max beauty for an increasing subsequence ending with height
st = PointAssignRangeMax(dp)
for i in range(len(heights)):
  ht = heights[i]
  bt = beauties[i]
  maxBefore = st.queryMax(0, ht - 1) # max beauty before
  newPotentialBeauty = maxBefore + bt
  if st.pointQuery(ht) < newPotentialBeauty:
    st.pointAssign(ht, newPotentialBeauty)

print(st.queryMax(0, len(dp) - 1))



