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

H, W, N = MII()
coords = [] # row, col, starting from the top, 1-indexed
for _ in range(N):
  coords.append(tuple(MII()))
coords.sort()
coords.append((H, W))

dp = [0] * (len(coords)) # # of ways to end at the i-th point

dfs, hashing, timeit = False, False, False

if dfs:
    from types import GeneratorType

    def bootstrap(f, stack=[]):
        def wrappedfunc(*args, **kwargs):
            if stack:
                return f(*args, **kwargs)
            else:
                to = f(*args, **kwargs)
                while True:
                    if type(to) is GeneratorType:
                        stack.append(to)
                        to = next(to)
                    else:
                        stack.pop()
                        if not stack:
                            break
                        to = stack[-1].send(to)
                return to
        return wrappedfunc

if hashing:
    RANDOM = random.getrandbits(20)
    class Wrapper(int):
        def __init__(self, x):
            int.__init__(x)

        def __hash__(self):
            return super(Wrapper, self).__hash__() ^ RANDOM

if True:
    import time
    def timer(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f'Time Used: {round((end - start) * 1000)} ms')
            return result
        return wrapper if timeit else func
# template by: https://github.com/agrawalishaan/leetcode

# n in the constructor is basically the biggest number we will operate on. So for instance finding n! % MOD. But also things like interleaving two sequences of length 500 and length 700 would require n=1200. To be safe, can always just put a big number like 1e5.
class ModCalc:
    def __init__(self, n, primeMod):
        self.n = n
        self.mod = primeMod # If this is not prime, anything using modInv may break (fermat's little theorem)
        # O(n) time to build a factorial mod array
        self.factorialsWithMod = self._buildFactorialsWithMod()
        # O(n) time to build an inverse factorial mod array
        self.inverseFactorialsWithMod = self._buildInverseFactorialsWithMod()

    # ********** STUFF WITH FACTORIALS **********

    # O(n) time to build a factorial mod array
    def _buildFactorialsWithMod(self):
        factorialsWithMod = [1] # 0 factorial is 1
        for factorial in range(1, self.n + 1):
            factorialsWithMod.append(factorialsWithMod[-1] * factorial % self.mod)
        return factorialsWithMod

    # O(n) time to build an inverse factorial mod array
    def _buildInverseFactorialsWithMod(self):
        inverseFactorialsWithMod = [1] * (self.n + 1)
        inverseFactorialsWithMod[self.n] = self.modInv(self.factorialsWithMod[self.n])
        for i in range(self.n - 1, 0, -1):
            inverseFactorialsWithMod[i] = inverseFactorialsWithMod[i + 1] * (i + 1) % self.mod
        return inverseFactorialsWithMod

    # Gets (x! % MOD)
    # O(1) time
    def getFactorialWithMod(self, factorial):
        return self.factorialsWithMod[factorial]

    # Gets (1/x! % MOD)
    # O(1) time
    def getInverseFactorialWithMod(self, inverseFactorial):
        return self.inverseFactorialsWithMod[inverseFactorial]

    # Given two sequences of length X and Y, such as "123" and "4567", find the # of ways to interleave them.  Note we don't care about the actual items in each sequence, we just care about the # of ways we can interleave the two. We don't even get the actual sequences themselves, just their lengths.
    # O(1) time
    def interleaveTwoSequencesWithMod(self, length1, length2):
        # Interleaving a sequence of length 3 and 4 would be like 7!/(3!4!), which is 7! * (1/3!) * (1/4!)
        combinedLength = length1 + length2
        if combinedLength >= len(self.factorialsWithMod):
            raise ValueError(f"To interleave {length1} and {length2} items, we need at least {combinedLength + 1} items in the factorial array.")
        numerator = self.getFactorialWithMod(combinedLength)
        denominator1 = self.getInverseFactorialWithMod(length1)
        denominator2 = self.getInverseFactorialWithMod(length2)
        return self.modMultiply(numerator, denominator1, denominator2)


    # Calculates the # of ways to select k items from n unique items. Order does not matter.
    # Formula for C(n, k) = n! / (k!(n-k)!)
    # Denominator is 1/k! * 1/(n-k)!
    # O(1) time
    def nChooseKWithMod(self, n, k):
        if k > n:
            return 0
        numerator = self.getFactorialWithMod(n)
        denominator1 = self.getInverseFactorialWithMod(k)
        denominator2 = self.getInverseFactorialWithMod(n - k)
        return self.modMultiply(numerator, denominator1, denominator2)

    # Calculates the # of ways to select k items from n unique items. Order matters.
    # Formula for P(n, k) = n! / (n-k)!
    # Denominator is 1/(n-k)!
    # O(1) time
    def nPermuteKWithMod(self, n, k):
        if k > n:
            return 0
        numerator = self.getFactorialWithMod(n)
        denominator = self.getInverseFactorialWithMod(n - k)
        return self.modMultiply(numerator, denominator)

    # Calculate the # of ways to distribute n identical items into k distinct buckets (relates to stars and bars)
    # Formula for allowing empty buckets is C(n+k-1, k-1), which is: (n+k-1)! * 1/(n-1)! * 1/k!
    # Formula for NOT allowing empty buckets is C(n-1, k-1), which is: (n-1)! * 1/(n-k)! * 1/k!
    # O(1) time
    def waysToPutIdenticalItemsIntoDistinctBucketsWithMod(self, items, buckets, allowEmptyBuckets=True):
        if allowEmptyBuckets:
            return self.nChooseKWithMod(items + buckets - 1, buckets - 1)
        return self.nChooseKWithMod(items - 1, buckets - 1)

    # Putting n distinct items into k distinct buckets is just k options for the first item, k for the second, etc, so k^n. This is if we allow empty buckets. If we don't allow empty buckets, we need Stirling numbers of the second kind.
    # O(log items) time due to modPow, but modPow can be cached
    def waysToPutDistinctItemsIntoDistinctBucketsAllowingEmptyWithMod(self, items, buckets):
        return self.modPow(buckets, items)

    def waysToPutDistinctItemsIntoDistinctNonemptyBucketsWithMod(self, items, buckets):
        # need to figure out how to do this in O(1) if it is possible lol
        pass

    # Calculates the # of monotone (right / up) paths from (1,1) to (height,width)
    # O(1) time
    def gridPathsWithMod(self, height, width):
        downMoves = height - 1
        rightMoves = width - 1
        totalMoves = downMoves + rightMoves
        if totalMoves >= len(self.factorialsWithMod):
            raise ValueError(f"To traverse a {height}×{width} grid we need at least {totalMoves + 1} items in the factorial array.")
        return self.nChooseKWithMod(totalMoves, downMoves)

    # ********** NO FACTORIALS NEEDED **********

    # Multiples k numbers together
    # O(k) time
    def modMultiply(self, *args):
        result = 1
        for num in args:
            result = (result * num) % self.mod
        return result

    # Calculates base^exponent % MOD
    # Can add caching if we are using the same base a lot. But if we are using one instance of the ModCalc class across all test cases, maybe that would MLE? I think no cache by default is better, since it is very fast already.
    # O(log exponent) time (even without caching)
    # @cache # uncomment to cache
    def modPow(self, base, exponent):
        return pow(base, exponent, self.mod)

    # Gets 1/x % MOD
    # Could cache this, if we are calling the same range of numbers a lot. If this class is created once across all test cases, could maybe MLE? Also num needs to be coprime to MOD.
    # O(log MOD) time
    # @cache # uncomment to cache
    def modInv(self, num):
        return self.modPow(num, self.mod - 2)


MOD = 10**9 + 7
calc = ModCalc(2*10**5 + 1, MOD)

for i, (r, c) in enumerate(coords):
  normalWays = calc.gridPathsWithMod(r, c)
  for j in range(i):
    prevR, prevC = coords[j]
    if prevR <= r and prevC <= c:
      prevWays = dp[j]
      fromPrevToHere = calc.gridPathsWithMod(r - prevR + 1, c - prevC + 1)
      normalWays -= (prevWays * fromPrevToHere)
  normalWays %= MOD
  dp[i] = normalWays

print(dp[-1])


