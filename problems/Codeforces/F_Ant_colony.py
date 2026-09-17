# Problem: F. Ant colony
# Contest: Codeforces - Codeforces Round 271 (Div. 2)
# URL: https://codeforces.com/problemset/problem/474/F?csrf_token=3cb15b6c3ef50adc042034ef50168a16
# Memory Limit: 256 MB
# Time Limit: 1000 ms
# 
# Powered by CP Editor (https://cpeditor.org)

import sys
input = sys.stdin.readline
import math
import collections
import bisect

n = int(input())
arr = list(map(int, input().split()))
t = int(input())
queries = [tuple(map(int, input().split())) for _ in range(t)]
# print(f'arr: {arr}')

# Supports range gcd, point assignment
# Iterative tree with 2*N memory, left child = 2*i, right child = 2*i+1

# build: O(n)
# range gcd: O(log n log max)
# point assignment: O(log n log max)
# point query: O(1)
class PointAssignRangeGcd:
  # O(n * log max) build tim
  def __init__(self, arr):
    self.n = len(arr)
    self.arr = arr
    self.tree = [0] * (2 * self.n)

    # build leaves
    for i in range(self.n):
      self.tree[self.n + i] = self.arr[i]

    # build internal nodes
    # each gcd call is O(log max), and there are roughly n of them
    for i in range(self.n - 1, 0, -1):
      self.tree[i] = math.gcd(self.tree[2 * i], self.tree[2 * i + 1])

  # O(log N * log max) update time (gcd is O(log max))
  def pointAssign(self, index, newVal):
    pos = index + self.n
    self.tree[pos] = newVal

    pos //= 2
    while pos:
      self.tree[pos] = math.gcd(self.tree[2 * pos], self.tree[2 * pos + 1])
      pos //= 2

  # O(log N * log max) update time (gcd is O(log max))
  def pointAssignAndMutateArray(self, index, val):
    self.arr[index] = val
    pos = index + self.n
    self.tree[pos] = val

    pos //= 2
    while pos:
      self.tree[pos] = math.gcd(self.tree[2 * pos], self.tree[2 * pos + 1])
      pos //= 2

  # O(1) time
  def pointQuery(self, index):
    return self.tree[self.n + index]

  # O(log N * log max) time (gcd is O(log max))
  def queryGcd(self, l, r):
    res = 0  # gcd(x, 0) = x
    l += self.n
    r += self.n

    while l <= r:
      if (l & 1) == 1:
        res = math.gcd(res, self.tree[l])
        l += 1
      if (r & 1) == 0:
        res = math.gcd(res, self.tree[r])
        r -= 1
      l //= 2
      r //= 2

    return res
st = PointAssignRangeGcd(arr)
valToIdxs = collections.defaultdict(list)
for i, v in enumerate(arr):
	valToIdxs[v].append(i)
# print(valToIdxs)

def count_in_range(sorted_arr, L, R):
    left = bisect.bisect_left(sorted_arr, L)   # first index ≥ L
    right = bisect.bisect_right(sorted_arr, R) # first index > R
    return right - left

def findAppearances(number, l, r):
	if not number in valToIdxs:
		return 0
	l -= 1
	r -= 1
	return count_in_range(valToIdxs[number], l, r)
	

# print(f'queries: {queries}')
for l, r in queries:
	g = st.queryGcd(l-1, r-1)
	appears = findAppearances(g, l, r)
	print((r - l + 1) - appears)
	# find how many times that gcd appears in that range