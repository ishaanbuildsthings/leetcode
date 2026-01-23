if True:
    from io import BytesIO, IOBase
    import math

    import random
    import sys
    import os

    import bisect
    import typing
    from collections import Counter, defaultdict, deque
    from copy import deepcopy
    from functools import cmp_to_key, lru_cache, reduce
    from heapq import heapify, heappop, heappush, heappushpop, nlargest, nsmallest
    from itertools import accumulate, combinations, permutations, count
    from operator import add, iand, ior, itemgetter, mul, xor
    from string import ascii_lowercase, ascii_uppercase, ascii_letters
    from typing import *
    BUFSIZE = 4096

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

    sys.stdin = IOWrapper(sys.stdin)
    sys.stdout = IOWrapper(sys.stdout)
    input = lambda: sys.stdin.readline().rstrip("\r\n")

    def I():
        return input()

    def II():
        return int(input())

    def MII():
        return map(int, input().split())

    def LI():
        return list(input().split())

    def LII():
        return list(map(int, input().split()))

    def GMI():
        return map(lambda x: int(x) - 1, input().split())

    def LGMI():
        return list(map(lambda x: int(x) - 1, input().split()))

    inf = float('inf')

class MaxSegTree:
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1
        self.size = size

        tree = [float("-inf")] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            left = tree[idx << 1]
            right = tree[(idx << 1) | 1]
            tree[idx] = left if left >= right else right
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = float("-inf")
        while l < r:
            if l & 1:
                v = tree[l]
                ans = v if v >= ans else ans
                l += 1
            if r & 1:
                r -= 1
                v = tree[r]
                ans = v if v >= ans else ans
            l >>= 1
            r >>= 1
        return ans

    def queryMax(self, l, r):
        return self._queryHalfOpen(l, r + 1)

    def pointUpdateAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            left = tree[pos << 1]
            right = tree[(pos << 1) | 1]
            tree[pos] = left if left >= right else right
            pos >>= 1

fmin = lambda x, y: x if x < y else y
fmax = lambda x, y: x if x > y else y
from collections import defaultdict
t = II()
for _ in range(t):
    n = II()
    A = LII()
    # start at tall trees, record max height reachable

    # we are at a shorter tree, every taller tree has been processed
    # anything to our left is reachable so we could reach the max height from there

    # but there are future shorter trees to our right
    # we should find the rightmost tree on our right shorter than us, then take the maximum before that

    suffMin = [10000000000] * n
    curr = 10000000000
    for i in range(n - 1, -1, -1):
        curr = fmin(curr, A[i])
        suffMin[i] = curr
    

    # find the rightmost tree on our right shorter than us, exclusive index
    rightmost = [None] * n
    for i in range(n - 1):
        l = i + 1
        r = n - 1
        resI = None
        while l <= r:
            m = (r + l) // 2
            if suffMin[m] < A[i]:
                resI = m
                l = m + 1
            else:
                r = m - 1
        rightmost[i] = resI
    
    A2 = [(x, i) for i, x in enumerate(A)]
    A2.sort(reverse=True)
    
    # we need to supportp point update in range and range max
    st = MaxSegTree([0] * n)

    for x, i in A2:
        right = rightmost[i] if rightmost[i] is not None else i
        bigBefore = fmax(x, st.queryMax(0, right))
        st.pointUpdateAndMutateArray(i, bigBefore)
        
    
    res = []
    for i in range(n):
        res.append(st.queryMax(i, i))
    print(*res)



    # 2 3 1 4

    # _ _ _ 4

    # _ 3 _ 4

    # 3 3 _ 4

    # 3 3 3 4