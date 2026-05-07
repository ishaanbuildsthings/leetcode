standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 0, 0, 0
de = 1
 
if 1:
 
    if standard_input:
        import io, os, sys
        input = lambda: sys.stdin.readline().strip()
 
        import math
        inf = math.inf
 
        def I():
            return input()
 
        def II():
            return int(input())
 
        def MII():
            return map(int, input().split())
 
        def LI():
            return input().split()
 
        def LII():
            return list(map(int, input().split()))
 
        def LFI():
            return list(map(float, input().split()))
 
        def GMI():
            return map(lambda x: int(x) - 1, input().split())
 
        def LGMI():
            return list(map(lambda x: int(x) - 1, input().split()))
 
    if packages:
        from io import BytesIO, IOBase
 
        import random
        import os
 
        import bisect
        import typing
        from collections import Counter, defaultdict, deque
        from copy import deepcopy
        from functools import cmp_to_key, lru_cache, reduce
        from heapq import merge, heapify, heappop, heappush, heappushpop, nlargest, nsmallest
        from itertools import accumulate, combinations, permutations, count, product
        from operator import add, iand, ior, itemgetter, mul, xor
        from string import ascii_lowercase, ascii_uppercase, ascii_letters
        from typing import *
        BUFSIZE = 4096
 
    if output_together:
        class FastIO(IOBase):
            newlines = 0
 
            def __init__(self, file):
                self._fd = file.fileno()
                self.buffer = BytesIO()
                self.writable = "x" in file.mode or "r" not in file.mode
                self.write = self.buffer.write if self.writable else None
 
            def read(self):
                while True:
                    b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                    if not b:
                        break
                    ptr = self.buffer.tell()
                    self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
                self.newlines = 0
                return self.buffer.read()
 
            def readline(self):
                while self.newlines == 0:
                    b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                    self.newlines = b.count(b"\n") + (not b)
                    ptr = self.buffer.tell()
                    self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
                self.newlines -= 1
                return self.buffer.readline()
 
            def flush(self):
                if self.writable:
                    os.write(self._fd, self.buffer.getvalue())
                    self.buffer.truncate(0), self.buffer.seek(0)
 
        class IOWrapper(IOBase):
            def __init__(self, file):
                self.buffer = FastIO(file)
                self.flush = self.buffer.flush
                self.writable = self.buffer.writable
                self.write = lambda s: self.buffer.write(s.encode("ascii"))
                self.read = lambda: self.buffer.read().decode("ascii")
                self.readline = lambda: self.buffer.readline().decode("ascii")
 
        sys.stdout = IOWrapper(sys.stdout)
 
    if dfs:
        from types import GeneratorType
 
        def bootstrap(f, stk=[]):
            def wrappedfunc(*args, **kwargs):
                if stk:
                    return f(*args, **kwargs)
                else:
                    to = f(*args, **kwargs)
                    while True:
                        if type(to) is GeneratorType:
                            stk.append(to)
                            to = next(to)
                        else:
                            stk.pop()
                            if not stk:
                                break
                            to = stk[-1].send(to)
                    return to
            return wrappedfunc
 
    if hashing:
        RANDOM = random.getrandbits(20)
        class Wrapper(int):
            def __init__(self, x):
                int.__init__(x)
 
            def __hash__(self):
                return super(Wrapper, self).__hash__() ^ RANDOM
 
    if read_from_file:
        file = open("input.txt", "r").readline().strip()[1:-1]
        fin = open(file, 'r')
        input = lambda: fin.readline().strip()
        output_file = open("output.txt", "w")
        def fprint(*args, **kwargs):
            print(*args, **kwargs, file=output_file)
 
    if de:
        def debug(*args, **kwargs):
            # print('\033[92m', end='')
            print(*args, **kwargs)
            # print('\033[0m', end='')
    else:
        def debug(*args, **kwargs):
            pass
 
 
    fmax = lambda x, y: x if x > y else y
    fmin = lambda x, y: x if x < y else y
 
    class lst_lst:
        def __init__(self, n) -> None:
            self.n = n
            self.pre = []
            self.cur = []
            self.notest = [-1] * (n + 1)
 
        def append(self, i, j):
            self.pre.append(self.notest[i])
            self.notest[i] = len(self.cur)
            self.cur.append(j)
 
        def iterate(self, i):
            tmp = self.notest[i]
            while tmp != -1:
                yield self.cur[tmp]
                tmp = self.pre[tmp]
 
n = II()
arr = LII()
 
comp = {} # num -> compressed
 
allVals = sorted(list(set(arr)))
for i, v in enumerate(allVals):
    comp[v] = i
 
# debug(comp)
 
endings = [0] * len(comp) # how many subsequences end in the compressed val
 
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
 
st = PointAssignRangeSum(endings)
MOD = 10**9 + 7
for i, v in enumerate(arr):
    c = comp[v]
    # debug(c)
    old = st.pointQuery(c)
    if c:
        prevEndings = st.querySum(0,c-1)
        st.pointAssignAndMutateArray(c, (prevEndings + 1 + old) % MOD)
    else:
        st.pointAssignAndMutateArray(c, 1 + old)
    # print(st.arr)
 
print(st.querySum(0, len(endings)-1) % MOD)
 
 
# 10
 
# 3
 
# 9
# 3 9
 
# 5
# 3 5
 
# 2
 
# 3 10
# 9 10
# 3 9 10
# 5 10
# 3 5 10
# 2 10
# 10
 
# 3 5
# 2 5
# 5
 
# 3 9
# 5 9
# 3 5 9
# 2 9
# 3 5 9
# 2 9
# 5 9
# 9
 
# 2
