standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 1, 0, 0
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

# Works on strings and arrays
class PalindromeHashing:
    # List of good prime numbers for hashing, will choose randomly if not provided
    GOOD_MODS = [1000000007, 1000000009, 998244353, 999999937, 999999929,
                 999999893, 999999797, 999999761, 999999757, 999999751,
                 999999739, 999999733, 999999721, 999999697, 999999691,
                 999999679, 999999673, 999999661, 999999649, 999999637,
                 999999631, 999999587, 999999599, 999999577, 999999563,
                 999999527, 999999519, 999999503, 999999491, 999999487]

    # O(n) time
    # Base is ideally prime, and bigger than the max value hashFunc can output, otherwise we can get collisions e.g. base=3, [1,1] collides with [4]. Base should also be coprime to mod I think?
    def __init__(self, stringOrArr: str, base: int = 911, mod: int = None, hashFunc=ord):
        self.window = list(stringOrArr)
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.hashFunc = hashFunc # The output coefficient for a single value, like ord('a')
        self.prefixHashes = self._buildPrefixHashes(stringOrArr) # O(n) time
        self.reversePrefixHashes = self._buildReversePrefixHashes(stringOrArr) # O(n) time
        self.basePow = self._precomputeBasePowers(len(stringOrArr)) # O(n) time

    # Builds the prefix hashes of the string/array, prefixHashes[i] is for string[:i], so prefixHashes[0] is for the empty string/array
    # O(n) time
    def _buildPrefixHashes(self, stringOrArr: str):
        prefixHashes = [0] * (len(stringOrArr) + 1)
        for i in range(1, len(stringOrArr) + 1):
            prefixHashes[i] = (prefixHashes[i - 1] * self.base + self.hashFunc(stringOrArr[i - 1])) % self.mod
        return prefixHashes

    # Builds the prefix hashes of the reversed string/array, so reversedPrefixHashes[2] is the hash of the first two character prefix, but that prefix is reversed. reversedPrefixHashes[0] is for the empty string
    # string = 'abc', reverse prefixes are 'a', 'ba', 'cba'
    # O(n) time
    def _buildReversePrefixHashes(self, stringOrArr: str):
        reversePrefixHashes = [0] * (len(stringOrArr) + 1)
        for i in range(1, len(stringOrArr) + 1):
            reversePrefixHashes[i] = (reversePrefixHashes[i - 1] * self.base + self.hashFunc(stringOrArr[-i])) % self.mod
        return reversePrefixHashes

    # Precompute powers of base, so base^0 % MOD, base^1 % MOD, base^2 % MOD, ...
    # O(n) time
    def _precomputeBasePowers(self, length: int):
        basePow = [1] * (length + 1)
        for i in range(1, length + 1):
            basePow[i] = (basePow[i - 1] * self.base) % self.mod
        return basePow

    # Gets the hash of a substring/subarray [left...right] using math
    # O(1) time
    def getHashForSubstring(self, left: int, right: int) -> int:
        return (self.prefixHashes[right + 1] - self.prefixHashes[left] * self.basePow[right - left + 1]) % self.mod

    # Gets the hash of a reversed section of the string/array, uses the original string/array indices
    # O(1) time
    def getHashForReversedSubstring(self, originalStringLeft: int, originalStringRight: int) -> int:
        left = len(self.window) - originalStringRight - 1
        right = len(self.window) - originalStringLeft
        return (self.reversePrefixHashes[right] - self.reversePrefixHashes[left] * self.basePow[right - left]) % self.mod

    # O(1) time
    def isPalindrome(self, left: int, right: int) -> bool:
        return self.getHashForSubstring(left, right) == self.getHashForReversedSubstring(left, right)

    # Gets the hash of a string/array
    # O(n) time
    def hash(self, stringOrArr: str) -> int:
        res = 0
        for c in stringOrArr:
            coefficient = self.hashFunc(c)
            res = (res * self.base + coefficient) % self.mod
        return res

    # Adds a character to the end of the string/array and updates hashes
    # O(1) time
    def addChar(self, c: str):
        self.window.append(c)
        if len(self.window) >= len(self.basePow):
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)
        self.prefixHashes.append((self.prefixHashes[-1] * self.base + self.hashFunc(c)) % self.mod)
        self.reversePrefixHashes.append((self.reversePrefixHashes[-1] * self.base + self.hashFunc(c)) % self.mod)

    # Removes the last character from the string/array and updates hashes
    # O(1) time
    def popChar(self):
        if len(self.window) == 0:
            return
        self.window.pop()
        self.prefixHashes.pop()
        self.reversePrefixHashes.pop()

    # Gets the hash of the entire window
    # O(1) time
    def getHash(self) -> int:
        return self.prefixHashes[-1]

    # Returns the current window as a list
    # O(1) time
    def getCurrentWindow(self) -> str:
        return self.window

    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return len(self.window)


n = II()
es = defaultdict(list)
children = defaultdict(list)
for i in range(n - 1):
    node = i + 2
    parent, string = LI()
    parent = int(parent)
    # print(f'{parent=} {string=} {node=}')
    es[(parent, node)] = string
    children[parent].append(node)
targetString = I()
# print(f'{targetString=}')
# print(f'{children=}')


h = PalindromeHashing('', mod=10**9 + 7)
target = PalindromeHashing(targetString, mod=10**9 + 7)

def isSuff():
    if h.length() < target.length():
        return False
    length = h.length()
    r = length - 1
    tLength = len(targetString)
    l = r - tLength + 1
    # print(f'{l=} {r=} h length: {length=}')
    suff = h.getHashForSubstring(l, r)
    return suff == target.getHash()


res = 0
@bootstrap
def dfs(node):
    global res
    for child in children[node]:
        stringEdge = es[(node, child)]
        # print(f'string edge: {stringEdge}')
        for c in stringEdge:
            h.addChar(c)
            res += isSuff()
        yield dfs(child)
        for c in stringEdge:
            h.popChar()
    yield None

dfs(1)

print(res)
 