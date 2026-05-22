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


# Iterative tree with 2*N memory, left child = 2*i, right child = 2*i + 1
#
# Complexities:
#   Build: O(n)
#   Space: O(n)
#   Query/Update: O(log n)
#
# baseFn:    function(value) -> nodeValue
# combineFn: function(leftVal, rightVal) -> newValue
class SegmentTree:
    def __init__(self, arr, baseFn, combineFn):
        self.n = len(arr)
        self._baseFn = baseFn
        self._combine = combineFn

        self.N = self.n
        self.tree = [None] * (2 * self.N)

        # Build leaves at indices [N..2N-1]
        for i in range(self.N):
            self.tree[self.N + i] = self._baseFn(arr[i])

        # Build internal nodes at [1..N-1]
        for i in range(self.N - 1, 0, -1):
            leftVal = self.tree[i << 1]
            rightVal = self.tree[(i << 1) | 1]
            self.tree[i] = self._combine(leftVal, rightVal)

    # O(log n)
    # TODO: THIS IS BUGGED RN IM NOT MUTATING THE ARRAY
    def updateAndMutateArray(self, index, newVal):
        # Update the leaf
        pos = self.N + index
        self.tree[pos] = self._baseFn(newVal)

        # Recompute internals up to the root
        pos >>= 1
        while pos:
            leftVal = self.tree[pos << 1]
            rightVal = self.tree[(pos << 1) | 1]
            self.tree[pos] = self._combine(leftVal, rightVal)
            pos >>= 1

    # O(log n)
    def query(self, l, r):
        l += self.N
        r += self.N
        leftRes = None
        rightRes = None

        while l <= r:
            # If l is a right child, use tree[l] and move to next
            if (l & 1) == 1:
                if leftRes is None:
                    leftRes = self.tree[l]
                else:
                    leftRes = self._combine(leftRes, self.tree[l])
                l += 1

            # If r is a left child, use tree[r] and move to previous
            if (r & 1) == 0:
                if rightRes is None:
                    rightRes = self.tree[r]
                else:
                    rightRes = self._combine(self.tree[r], rightRes)
                r -= 1

            l >>= 1
            r >>= 1

        if leftRes is None:
            return rightRes
        if rightRes is None:
            return leftRes
        return self._combine(leftRes, rightRes)

s = I()
q = II()
arr = list(s)
# print(f'{arr=}')
def base(v):
  return 1 << (ord(v) - ord('a'))
def combine(a, b):
  return a | b

seg = SegmentTree(arr, base, combine)
for _ in range(q):
  op, x, y = LI()
  # print(f'op is: {op}')
  op = int(op)
  # print(f'{x=}, {y=}')
  if op == 1:
    seg.updateAndMutateArray(int(x) - 1, y)
  else:
    # print(f'hmmm: {x}, {y}')
    x = int(x)
    y = int(y)
    print(seg.query(x-1,y-1).bit_count())