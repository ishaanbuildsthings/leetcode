# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rolling-hash-palindrome/template.py
# @operations: append getAll hashAll isPalindrome longestPalCenteredAtI longestPalCenteredAtIPlusOne pointGet pop rangeHash rangeHashReversed rangesEqual size
# @data-structure-type: rolling-hash
# @letters: same
# @complexities:
#   append: 1
#   getAll: N
#   isPalindrome: 1
#   pointGet: 1
#   pop: 1
#   rangeHash: 1
#   rangeHashReversed: 1
#   rangesEqual: 1
#   size: 1
#   hashAll: 1
#   longestPalCenteredAtI: log(N)
#   longestPalCenteredAtIPlusOne: log(N)
#   build: N
# @memory:
#   layout: none
#   node: back[1*N] P[1*N] RB[1*N]
#   tags: none
#   other: pw[1*N] pwi[1*N]
#   note: prefix hashes read both ways; the right end only, so every op is O(1) worst case

# Rolling hashes read both ways over a window that grows and shrinks at the right end: range hashes, reversed range
# hashes and palindrome checks in O(1) worst case (the longest palindrome around a centre by binary search).
# Values are numbers or single characters (then they hash by their code). All indices 0-based, ranges inclusive.
# Hashes: polynomial, mod a prime (2^61 - 1 unless you pass one) with a base drawn at random once per run and shared by
# every structure in it, so hashes compare across structures; a base and mod passed to the constructor are that
# structure's own. The base needs no relation to the alphabet: with a 61-bit prime mod and a random base, collisions
# are chance (about 2^-61 per comparison), not structure.
#
# Usage:
#     arr = [3, 1, 4, 1, 5]
#     base, mod = 911, 10**9 + 7                                              # set these only to match something else
#     (unset, they are shared between structures, so hashes compare)
#     t1 = RollingHashPalindrome(arr)                                         # the defaults: hashing just works for
#     negatives, large numbers, chars, with the run's random base
#     t0 = RollingHashPalindrome()                                            # or start empty
#     t2 = RollingHashPalindrome(arr, hashBase=base)                          # your base, mod 2^61 - 1
#     t3 = RollingHashPalindrome(arr, hashMod=mod)                            # the run's random base, your mod
#     t4 = RollingHashPalindrome(arr, hashBase=base, hashMod=mod)             # both
#     s = RollingHashPalindrome("abacaba")                                    # a string works too (values are its
#     characters)
#     t1.rangeHash(0, 2) == RollingHashPalindrome([3, 1, 4]).rangeHash(0, 2)  # True: the same values, base and mod (the
#     run's)
import random


_HP = (1 << 61) - 1  # the default mod: a prime
# the run's random base, drawn once when the program starts: no test can be built against it, and every structure in the
# run hashes with it, so their hashes compare (two of these templates pasted into one file share this one variable)
_HB = random.randrange(1 << 40, _HP - 1)


class RollingHashPalindrome:
    # O(N) -- arr: the initial array (a list of ints, negatives included, or a string / list of single characters), or
    # left out to start empty. Hashing just works with the defaults: any 64-bit values, negatives and characters, with
    # the run's random base (shared by every structure of the run, so their hashes compare) and the prime mod 2^61 - 1.
    # Set hashBase / hashMod only to match something else: then every value must be below the mod (a value v hashes as
    # v + 1, so a 0 is not nothing), the mod a prime, and the base in [2, mod - 2]
    def __init__(self, arr=(), hashBase=None, hashMod=None):
        self.mod = _HP if hashMod is None else hashMod
        self.base = (_HB if hashBase is None else hashBase) % self.mod
        self.inv = pow(self.base, self.mod - 2, self.mod)
        self.pw, self.pwi = [1], [1]  # pw[k] = base^k, pwi[k] = base^-k, grown as the window grows (amortized O(1))
        vals = list(arr)
        self._code = self._firstCode  # (characters hash by their code, numbers as they are: the first value decides)
        self.back = []
        self.P = []  # P[k]: hash of back[0..k] read left to right
        self.RB = []  # RB[k]: sum of hval(back[k]) * base^k: the back half read backwards
        for v in vals:
            self.append(v)

    # O(1) -- the current length of the window
    def size(self):
        return len(self.back)

    # O(N) -- the whole window as a list
    def getAll(self):
        return list(self.back)

    # O(1) -- a[i]; needs 0 <= i < size(), else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        return self.back[i]

    # O(1) -- append v at the right end
    def append(self, v):
        hv = (self._code(v) + 1) % self.mod
        k = len(self.back)
        self.P.append((self.P[-1] * self.base + hv) % self.mod if k else hv)
        pw = self._powers(k)[0]
        self.RB.append(((self.RB[-1] if k else 0) + hv * pw[k]) % self.mod)
        self.back.append(v)

    # O(1) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
        self.P.pop()
        self.RB.pop()
        return self.back.pop()

    # O(1) -- hash of a[l..r] read left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # 0 <= l <= r < size(), else raises IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHash: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._hash(l, r)

    # O(1) -- hash of a[l..r] read right to left (what rangeHash gives for the reversed range); needs
    # 0 <= l <= r < size(), else raises IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._hashRev(l, r)

    # O(1) -- is a[l..r] a palindrome (its two readings hash equal); needs 0 <= l <= r < size(), else raises IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._hash(l, r) == self._hashRev(l, r)

    # O(1) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs 0 <= l1 <= r1 < size() and
    # 0 <= l2 <= r2 < size(), else raises IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.size() and 0 <= l2 <= r2 < self.size()):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.size()}")
        return r1 - l1 == r2 - l2 and self._hash(l1, r1) == self._hash(l2, r2)

    # O(1) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    # this run, so it compares with another one's hashes); needs n >= 1, else raises IndexError
    def hashAll(self):
        if self.size() < 1:
            raise IndexError("hashAll: needs n >= 1")
        return self.rangeHash(0, self.size() - 1)

    # O(log(N)) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    # its radius, log N calls of isPalindrome; needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtI(self, i):
        n = self.size()
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtI: needs 0 <= i < n, got i = {i}, n = {n}")
        lo, hi = 0, min(i, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo, i + lo

    # O(log(N)) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty
    # range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    # needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        n = self.size()
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtIPlusOne: needs 0 <= i < n, got i = {i}, n = {n}")
        lo, hi = 0, min(i + 1, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid + 1, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo + 1, i + lo

    # ---- internals ----

    def _hash(self, x, y):  # hash of a[x..y] left to right
        P, pw = self.P, self._powers(y - x + 1)[0]
        return (P[y] - (P[x - 1] * pw[y - x + 1] if x else 0)) % self.mod

    def _hashRev(self, x, y):  # hash of a[y], a[y-1], ..., a[x]
        RB, pwi = self.RB, self._powers(x)[1]
        return (RB[y] - (RB[x - 1] if x else 0)) * pwi[x] % self.mod
    def _firstCode(self, v):  # the first value decides how values hash (so starting empty works): characters by code
        self._code = ord if isinstance(v, str) else int
        return self._code(v)

    def _powers(self, k):  # pw and pwi with at least k + 1 entries
        pw, pwi = self.pw, self.pwi
        if len(pw) <= k:
            base, inv, mod = self.base, self.inv, self.mod
            while len(pw) <= k:
                pw.append(pw[-1] * base % mod)
                pwi.append(pwi[-1] * inv % mod)
        return pw, pwi
