standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 0, 0, 0
deb = 0

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

t = II()
INF = 10**18

class WaveletTree:
    def __init__(self, data, minValue=None, maxValue=None):
        if not data:
            return
        if minValue is None:
            minValue = min(data)
        if maxValue is None:
            maxValue = max(data)
        self.lo = minValue
        self.hi = maxValue
        self.b = [0]
        if self.lo == self.hi:
            self.left = None
            self.right = None
            return
        mid = (self.lo + self.hi) // 2
        leftArr = []
        rightArr = []
        for x in data:
            if x <= mid:
                leftArr.append(x)
                self.b.append(self.b[-1] + 1)
            else:
                rightArr.append(x)
                self.b.append(self.b[-1])
        self.left = WaveletTree(leftArr, self.lo, mid)
        self.right = WaveletTree(rightArr, mid + 1, self.hi)

    def kth(self, l, r, k):
        if l > r or k < 1 or self.lo is None:
            return None
        if self.lo == self.hi:
            return self.lo
        inLeft = self.b[r + 1] - self.b[l]
        if k <= inLeft:
            newL = self.b[l]
            newR = self.b[r + 1] - 1
            return self.left.kth(newL, newR, k)
        else:
            newL = l - self.b[l]
            newR = r - self.b[r + 1]
            return self.right.kth(newL, newR, k - inLeft)

class CompressedWaveletTree:
    def __init__(self, data):
        vals = sorted(set(data))
        rank = {v: i for i, v in enumerate(vals)}
        compressed = [rank[x] for x in data]
        self.vals = vals
        self.tree = WaveletTree(compressed, 0, len(vals) - 1)

    def kth(self, l, r, k):
        idx = self.tree.kth(l, r, k)
        return self.vals[idx]

for _ in range(t):
    de('-----------')
    n, numSegs = LII()
    qs = []
    for zz in range(numSegs):
        l, r = LII()
        l-=1
        r-=1
        qs.append([l,r])
    q = II()
    assigns = []
    for zzz in range(q):
        i = II()
        i -= 1
        assigns.append(i)

    arr = [INF] * n
    de(f'{arr=}')
    de(f'{assigns=}')
    de(f'{qs=}')

    for k in range(len(assigns)):
        index = assigns[k]
        time = k + 1
        arr[index] = time

    de(f'arr after assigns: {arr}')

    wt = CompressedWaveletTree(arr)

    res = inf
    for l, r in qs:
        # de('--')
        # de(f'{l=} {r=}')
        width = r - l + 1
        reqChanges = width//2 + 1
        # de(f'{reqChanges=}')
        kthSmallest = wt.kth(l, r, reqChanges)
        res = fmin(res, kthSmallest)

    if res == INF:
        print(-1)
    else:
        print(res)

 