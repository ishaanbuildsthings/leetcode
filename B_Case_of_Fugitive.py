n, m = map(int, input().split())
standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 0, 0, 0
deb = 1
from math import inf

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

    if deb:
        def de(*args, **kwargs):
            # print('\033[92m', end='')
            print(*args, **kwargs)
            # print('\033[0m', end='')
    else:
        def de(*args, **kwargs):
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

class MinSegTree:
    def __init__(self, arr):
        self.arr = list(arr)
        self.n = len(arr)
        size = 1
        while size < self.n:
            size <<= 1
        self.size = size
        tree = [inf] * (2 * size)
        base = size
        for i, v in enumerate(arr):
            tree[base + i] = v
        for idx in range(size - 1, 0, -1):
            tree[idx] = min(tree[idx << 1], tree[(idx << 1) | 1])
        self.tree = tree

    def _queryHalfOpen(self, l, r):
        tree = self.tree
        l += self.size
        r += self.size
        ans = inf
        while l < r:
            if l & 1:
                if tree[l] < ans: ans = tree[l]
                l += 1
            if r & 1:
                r -= 1
                if tree[r] < ans: ans = tree[r]
            l >>= 1
            r >>= 1
        return ans

    # inf if l>r
    def queryMin(self, l, r):
        if l > r: return inf
        return self._queryHalfOpen(l, r + 1)

    def pointAssignAndMutateArray(self, index, newVal):
        self.arr[index] = newVal
        tree = self.tree
        pos = self.size + index
        tree[pos] = newVal
        pos >>= 1
        while pos:
            new = min(tree[pos << 1], tree[(pos << 1) | 1])
            if tree[pos] == new:
                break
            tree[pos] = new
            pos >>= 1     
    def leftmostLteX(self, l, r, x):
        tree = self.tree
        size = self.size
        l += size
        r += size + 1
        left_nodes = []
        right_nodes = []
        while l < r:
            if l & 1:
                left_nodes.append(l)
                l += 1
            if r & 1:
                r -= 1
                right_nodes.append(r)
            l >>= 1
            r >>= 1
        for node in left_nodes + right_nodes[::-1]:
            if tree[node] <= x:
                while node < size:
                    node <<= 1
                    if tree[node] > x:
                        node |= 1
                return node - size
        return -1

islands = []
for _ in range(n):
    L, R = MII()
    islands.append((L, R))

bridges = LII()
# print(f'{bridges=}')

ranges = []
for i in range(n - 1):
    l1, r1 = islands[i]
    l2, r2 = islands[i + 1]
    mn = l2 - r1
    mx = r2 - l1
    tup = (mn, mx, i)
    ranges.append(tup)

ranges.sort()
bridges = sorted((v, i + 1) for i, v in enumerate(bridges))

# print(f'{bridges=}')
# print(f'{ranges=}')

mns = [rg[0] for rg in ranges]
rs = [rg[1] for rg in ranges]
st = MinSegTree(rs)

assign = [0] * (n - 1)
filled = 0
ok = True
for b, bi in bridges:
    if filled == n - 1:
        break
    l = 0
    r = n - 2
    hi = -1
    while l <= r:
        mid = (l + r) // 2
        if mns[mid] <= b:
            hi = mid
            l = mid + 1
        else:
            r = mid - 1
    if hi == -1:
        continue
    mv = st.queryMin(0, hi)
    if mv == float("inf"):
        continue
    if mv < b:
        ok = False
        break
    pos = st.leftmostLteX(0, hi, mv)
    assign[ranges[pos][2]] = bi
    st.pointAssignAndMutateArray(pos, float("inf"))
    filled += 1

if not ok or filled < n - 1:
    print("No")
else:
    print("Yes")
    print(' '.join(str(x) for x in assign))