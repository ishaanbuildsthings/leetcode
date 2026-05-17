standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 0, 0, 0
deb = 1

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








# I GRABBED THIS TEMPLATE FROM HERE: https://github.com/cheran-senthil/PyRival/blob/master/pyrival/data_structures/SortedList.py
"""
The "sorted list" data-structure, with amortized O(n^(1/3)) cost per insert and pop.

Example:

A = SortedList()
A.insert(30)
A.insert(50)
A.insert(20)
A.insert(30)
A.insert(30)

print(A) # prints [20, 30, 30, 30, 50]

print(A.lower_bound(30), A.upper_bound(30)) # prints 1 4

print(A[-1]) # prints 50
print(A.pop(1)) # prints 30

print(A) # prints [20, 30, 30, 50]
print(A.count(30)) # prints 2

"""

from bisect import bisect_left as lower_bound
from bisect import bisect_right as upper_bound


# class FenwickTree:
#     def __init__(self, x):
#         bit = self.bit = list(x)
#         size = self.size = len(bit)
#         for i in range(size):
#             j = i | (i + 1)
#             if j < size:
#                 bit[j] += bit[i]

#     def update(self, idx, x):
#         """updates bit[idx] += x"""
#         while idx < self.size:
#             self.bit[idx] += x
#             idx |= idx + 1

#     def __call__(self, end):
#         """calc sum(bit[:end])"""
#         x = 0
#         while end:
#             x += self.bit[end - 1]
#             end &= end - 1
#         return x

#     def find_kth(self, k):
#         """Find largest idx such that sum(bit[:idx]) <= k"""
#         idx = -1
#         for d in reversed(range(self.size.bit_length())):
#             right_idx = idx + (1 << d)
#             if right_idx < self.size and self.bit[right_idx] <= k:
#                 idx = right_idx
#                 k -= self.bit[idx]
#         return idx + 1, k


# class SortedList:
#     block_size = 700

#     def __init__(self, iterable=()):
#         iterable = sorted(iterable)
#         self.micros = [iterable[i:i + self.block_size - 1] for i in range(0, len(iterable), self.block_size - 1)] or [[]]
#         self.macro = [i[0] for i in self.micros[1:]]
#         self.micro_size = [len(i) for i in self.micros]
#         self.fenwick = FenwickTree(self.micro_size)
#         self.size = len(iterable)

#     def insert(self, x):
#         i = lower_bound(self.macro, x)
#         j = upper_bound(self.micros[i], x)
#         self.micros[i].insert(j, x)
#         self.size += 1
#         self.micro_size[i] += 1
#         self.fenwick.update(i, 1)
#         if len(self.micros[i]) >= self.block_size:
#             self.micros[i:i + 1] = self.micros[i][:self.block_size >> 1], self.micros[i][self.block_size >> 1:]
#             self.micro_size[i:i + 1] = self.block_size >> 1, self.block_size >> 1
#             self.fenwick = FenwickTree(self.micro_size)
#             self.macro.insert(i, self.micros[i + 1][0])

#     def pop(self, k=-1):
#         i, j = self._find_kth(k)
#         self.size -= 1
#         self.micro_size[i] -= 1
#         self.fenwick.update(i, -1)
#         return self.micros[i].pop(j)

#     def __getitem__(self, k):
#         i, j = self._find_kth(k)
#         return self.micros[i][j]

#     def count(self, x):
#         return self.upper_bound(x) - self.lower_bound(x)

#     def __contains__(self, x):
#         return self.count(x) > 0

#     def lower_bound(self, x):
#         i = lower_bound(self.macro, x)
#         return self.fenwick(i) + lower_bound(self.micros[i], x)

#     def upper_bound(self, x):
#         i = upper_bound(self.macro, x)
#         return self.fenwick(i) + upper_bound(self.micros[i], x)

#     def _find_kth(self, k):
#         return self.fenwick.find_kth(k + self.size if k < 0 else k)

#     def __len__(self):
#         return self.size

#     def __iter__(self):
#         return (x for micro in self.micros for x in micro)

#     def __repr__(self):
#         return str(list(self))




class SortedList:
    def __init__(self, N):
        self.n = N + 1
        self.tree = [0] * (self.n + 1)
        self.cnt = [0] * (self.n + 1)
        self.size = 0
        self.LOG = self.n.bit_length()
    
    def insert(self, x):
        self.cnt[x] += 1
        self.size += 1
        i = x + 1
        while i <= self.n:
            self.tree[i] += 1
            i += i & -i
    
    def _remove_value(self, x):
        self.cnt[x] -= 1
        self.size -= 1
        i = x + 1
        while i <= self.n:
            self.tree[i] -= 1
            i += i & -i
    
    def lower_bound(self, x):
        s = 0
        i = x
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s
    
    def pop(self, idx):
        if idx < 0:
            idx += self.size
        pos = 0
        k = idx
        bit = 1 << (self.LOG - 1)
        while bit > 0:
            ni = pos + bit
            if ni <= self.n and self.tree[ni] <= k:
                pos = ni
                k -= self.tree[pos]
            bit >>= 1
        val = pos
        self._remove_value(val)
        return val
    
    def __getitem__(self, idx):
        if idx < 0:
            idx += self.size
        pos = 0
        k = idx
        bit = 1 << (self.LOG - 1)
        while bit > 0:
            ni = pos + bit
            if ni <= self.n and self.tree[ni] <= k:
                pos = ni
                k -= self.tree[pos]
            bit >>= 1
        return pos
    
    def __len__(self):
        return self.size
    
    def __bool__(self):
        return self.size > 0





import math
from collections import defaultdict
def solve():
    n = II()
    points = []
    for _ in range(n):
        x, y = LII()
        points.append((x, y))
    
    byX = defaultdict(list) # maps str(x) -> list of sorted ys
    byY = defaultdict(list)
    for x, y in points:
        byX[str(x)].append(y)
        byY[str(y)].append(x)
    for key in byX:
        byX[key].sort()
    for key in byY:
        byY[key].sort()
    
    allXs = list(byX.keys())
    allXs = sorted([int(x) for x in allXs])
    # print(f'{allXs=}')

    # how many are in (L...R) DOUBLE EXCLUSIVE
    def cnt(L, R):
        return lower_bound(allXs, R) - upper_bound(allXs, L)

    belowSl = SortedList(n + 10)
    aboveSl = SortedList(n + 10)
    for x, y in points:
        aboveSl.insert(x)
    
    res = 0

    allIntYs = sorted([int(y) for y in byY])
    for intY in allIntYs:
        if intY == allIntYs[-1]:
            break
        strY = str(intY)
        L = -1 * math.inf
        R = math.inf
        for intX in byY[strY]:
            belowSl.insert(intX)

            # remove from above
            idx = aboveSl.lower_bound(intX)
            aboveSl.pop(idx)

            
        if belowSl:
            L = belowSl[0]
        if aboveSl:
            L = max(L, aboveSl[0])
        
        if belowSl:
            R = belowSl[-1]
        if aboveSl:
            R = min(R, aboveSl[-1])
        
        if L < R:
            options = cnt(L, R) + 1
            res += options
    
    print(res)


        


    
    # we have boundaries with these L and R coordinates
    # so the number of vertical cuts is number of elements in (L, R) + 1
    # def cnt(L, R):
    
t = int(input())
for _ in range(t):
    solve()