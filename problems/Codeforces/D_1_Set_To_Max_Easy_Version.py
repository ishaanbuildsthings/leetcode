standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 0, 0, 0
de = 1

# we are going to apply range chmax queries
def basefn(v):
    return v
def combinefn(a, b):
    return fmax(a, b)
def applyLazyToValue(laz, v):
    return fmax(laz, v)
def combineLazies(a, b):
    return fmax(a,b)

# TODO: add point assignment
class LazyPropagationSegmentTree:
    __slots__ = ('n', 'N', 'height', 'tree', 'lazy', '_combine', '_applyAggregate', '_compose')

    def __init__(self, arr, baseFn, combineFn, applyLazyToValue, combineLazies):
        self.n = len(arr)
        self.N = 1 << ((self.n - 1).bit_length()) if self.n > 0 else 1
        self.height = self.N.bit_length() - 1
        self.tree = [0] * (2 * self.N)
        # lazy tags stored on internal nodes only
        self.lazy = [None] * self.N
        self._combine = combineFn
        self._applyAggregate = applyLazyToValue
        self._compose = combineLazies

        # build leaves
        for i in range(self.N):
            if i < self.n:
                self.tree[self.N + i] = baseFn(arr[i])
            else:
                # fill padded slots with base identity
                self.tree[self.N + i] = baseFn(0) # TODO: note this might be dangerous, I think we assume the identity value here is 0 which could be wrong? also I don't think we need this identity stuff for recursive trees, since in the recursive one we do not descend to a child if it isn't in ql...qr

        # build internals
        for i in range(self.N - 1, 0, -1):
            self.tree[i] = self._combine(self.tree[2*i], self.tree[2*i + 1])

    def _apply(self, idx, lazyVal):
        # apply lazyVal to node idx
        self.tree[idx] = self._applyAggregate(lazyVal, self.tree[idx])
        # if not leaf, compose tag
        if idx < self.N:
            old = self.lazy[idx]
            if old is None:
                self.lazy[idx] = lazyVal
            else:
                self.lazy[idx] = self._compose(old, lazyVal)

    def _pushDown(self, idx):
        # push tags from root->idx
        for h in range(self.height, 0, -1):
            i = idx >> h
            tag = self.lazy[i]
            if tag is not None:
                self._apply(2*i, tag)
                self._apply(2*i + 1, tag)
                self.lazy[i] = None

    def _pullUp(self, idx):
        # recompute internals idx->root
        idx >>= 1
        while idx:
            if self.lazy[idx] is None:
                self.tree[idx] = self._combine(self.tree[2*idx], self.tree[2*idx + 1])
            idx >>= 1

    def updateRange(self, l, r, lazyVal):
        if l > r:
            return
        l0 = l + self.N
        r0 = r + self.N

        # push down endpoints
        self._pushDown(l0)
        self._pushDown(r0)

        L, R = l0, r0

        # apply on segment
        while L <= R:
            if (L & 1):
                self._apply(L, lazyVal)
                L += 1
            if not (R & 1):
                self._apply(R, lazyVal)
                R -= 1
            L >>= 1; R >>= 1

        # pull up changes
        self._pullUp(l0)
        self._pullUp(r0)

    def queryPoint(self, idx):
        if idx < 0 or idx >= self.n:
            return None
        tree_idx = idx + self.N
        self._pushDown(tree_idx)
        return self.tree[tree_idx]

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


# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

# ✅ Tested thoroughly
# ⚠️ Not constant opimized
# ⚠️ Not using one template per-operation type (might reduce some small overhead?)
class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        log = [0] * (n + 1)
        for i in range(2, n + 1):
            log[i] = log[i // 2] + 1
        BITS = log[n] + 1
        sparse = [[None] * n for _ in range(BITS)]
        sparse[0][:] = nums
        for p in range(1, BITS):
            span = 1 << p
            half = span >> 1
            prev = sparse[p - 1]
            curr = sparse[p]
            for i in range(n - span + 1):
                curr[i] = combineFn(prev[i], prev[i + half])
        self.sparse = sparse
        self.log = log
        self.combineFn = combineFn

    def query(self, l, r):
        width = r - l + 1
        p = self.log[width]
        span = 1 << p
        row = self.sparse[p]
        return self.combineFn(row[l], row[r - span + 1])


def solve(a, b):

    n = len(a)
    # debug(f'{a=} {b=}')
    sparse = SparseTable(b, fmin)
    sa = SparseTable(a, fmax)
    st = LazyPropagationSegmentTree(a, basefn, combinefn, applyLazyToValue, combineLazies)

    # we want to find the furthest right and furthest left we can chmax without exceeding a value in B
    for i in range(len(a)):
        v = a[i]
        # find furthest right s.t. the min in that range is >= v
        left = i
        right = n - 1
        resI = None
        while left <= right:
            m = (right+left)//2
            mn = sparse.query(i, m)
            mx = sa.query(i, m)
            # print(f'mx in i...m for arr A is: {mx} for i={i} m={m}')
            if mn >= v and mx == v:
                resI = m
                left = m + 1
            else:
                right = m - 1

        # print(f'going right res i is: {resI}')

        # find furthest left s.t. min in that range is >= v
        left = 0
        right = i
        resI2 = None
        while left <= right:
            m = (right+left)//2
            mn = sparse.query(m, i)
            mx = sa.query(m, i)
            if mn >= v and mx==v:
                resI2 = m
                right = m - 1
            else:
                left = m + 1

        # print(f'resI2: {resI2} resI: {resI}')

        if resI is None or resI2 is None:
            continue



        st.updateRange(resI2, resI, v)

    for i in range(n):
        # print(f'point is: {st.queryPoint(i)}')
        if st.queryPoint(i) != b[i]:
            return False

    return True







t = II()
for i in range(t):
    # debug('----------')
    n = II()
    a = LII()
    b = LII()
    ans = solve(a, b)
    if ans:
        print('YES')
    else:
        print('NO')