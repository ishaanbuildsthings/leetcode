# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/rolling-hash-window/template.py
# @operations: append appendLeft getAll hashAll pointAdd pointAssign pointChmax pointChmin pointGet pop popLeft size
# @data-structure-type: rolling-hash
# @letters: same
# @complexities:
#   append: 1
#   appendLeft: 1
#   getAll: N
#   hashAll: 1
#   pointAdd: 1
#   pointAssign: 1
#   pointChmax: 1
#   pointChmin: 1
#   pointGet: 1
#   pop: 1 amortized
#   popLeft: 1 amortized
#   size: 1
#   build: N
# @memory:
#   layout: none
#   node: back[1*N] front[1*N]
#   tags: none
#   other: pw[1*N] pwi[1*N]
#   note: two lists (a front half stored reversed, a back half in order), the hash of the whole window kept up to date; nothing per range, so only hashAll

# Rolling hash of a window that grows and shrinks at both ends in O(1): the hash of the whole window (hashAll), point
# assign, and O(1) a[i]. The window is a front half stored reversed plus a back half in order.
# Values are numbers or single characters (then they hash by their code). All indices 0-based, ranges inclusive.
# Hashes: polynomial, mod a prime (2^61 - 1 unless you pass one) with a base drawn at random once per run and shared by
# every structure in it, so hashes compare across structures; a base and mod passed to the constructor are that
# structure's own. The base needs no relation to the alphabet: with a 61-bit prime mod and a random base, collisions
# are chance (about 2^-61 per comparison), not structure.
#
# Usage:
#     arr = [3, 1, 4, 1, 5]
#     base, mod = 911, 10**9 + 7                                    # set these only to match something else (unset, they are shared between structures, so hashes compare)
#     t1 = RollingHashWindow(arr)                                   # the defaults: hashing just works for negatives, large numbers, chars, with the run's random base
#     t0 = RollingHashWindow()                                      # or start empty
#     t2 = RollingHashWindow(arr, hashBase=base)                    # your base, mod 2^61 - 1
#     t3 = RollingHashWindow(arr, hashMod=mod)                      # the run's random base, your mod
#     t4 = RollingHashWindow(arr, hashBase=base, hashMod=mod)       # both
#     s = RollingHashWindow("abacaba")                              # a string works too (values are its characters)
#     t1.hashAll() == RollingHashWindow([3, 1, 4, 1, 5]).hashAll()  # True: the same values, base and mod (the run's)
import random


_HP = (1 << 61) - 1  # the default mod: a prime
# the run's random base, drawn once when the program starts: no test can be built against it, and every structure in the
# run hashes with it, so their hashes compare (two of these templates pasted into one file share this one variable)
_HB = random.randrange(1 << 40, _HP - 1)


class RollingHashWindow:
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
        self._code = ord if vals and isinstance(vals[0], str) else int  # (characters hash by their code)
        self.back = []
        self.front = []  # the first values, stored last to first
        self.h = 0  # the hash of the whole window
        for v in vals:
            self.append(v)

    # O(1) -- the current length of the window
    def size(self):
        return len(self.front) + len(self.back)

    # O(N) -- the whole window as a list
    def getAll(self):
        return self.front[::-1] + self.back

    # O(1) -- a[i]; needs 0 <= i < size(), else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        f = len(self.front)
        return self.front[f - 1 - i] if i < f else self.back[i - f]

    # O(1) -- append v at the right end
    def append(self, v):
        self.h = (self.h * self.base + self._code(v) + 1) % self.mod
        self.back.append(v)

    # O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    def appendLeft(self, v):
        n = self.size()
        self.h = (self.h + (self._code(v) + 1) * self._powers(n)[0][n]) % self.mod
        self.front.append(v)

    # O(1 amortized) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
        if not self.back:
            self._moveToBack()
        v = self.back.pop()
        self.h = (self.h - self._code(v) - 1) * self._powers(1)[1][1] % self.mod
        return v

    # O(1 amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        if not self.front:
            self._moveToFront()
        v = self.front.pop()
        n = self.size()
        self.h = (self.h - (self._code(v) + 1) * self._powers(n)[0][n]) % self.mod
        return v

    # O(1) -- a[i] = v (overwrite); needs 0 <= i < size(), else raises IndexError
    def pointAssign(self, i, v):
        n = self.size()
        if not 0 <= i < n:
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {n}")
        f = len(self.front)
        old = self.front[f - 1 - i] if i < f else self.back[i - f]
        self.h = (self.h + (self._code(v) - self._code(old)) * self._powers(n)[0][n - 1 - i]) % self.mod
        if i < f:
            self.front[f - 1 - i] = v
        else:
            self.back[i - f] = v

    # O(1) -- a[i] += v; needs 0 <= i < size(), else raises IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.pointAssign(i, self.pointGet(i) + v)

    # O(1) -- a[i] = max(a[i], v); needs 0 <= i < size(), else raises IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(1) -- a[i] = min(a[i], v); needs 0 <= i < size(), else raises IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.pointAssign(i, min(self.pointGet(i), v))

    # O(1) -- hash of the whole window a[0..size()-1] (left to right, the same base and mod as every structure this run
    # unless you passed your own, so it compares with their hashes); needs size() >= 1, else raises IndexError
    def hashAll(self):
        if self.size() < 1:
            raise IndexError("hashAll: needs size() >= 1")
        return self.h

    # ---- internals ----

    def _powers(self, k):  # pw and pwi with at least k + 1 entries
        pw, pwi = self.pw, self.pwi
        if len(pw) <= k:
            base, inv, mod = self.base, self.inv, self.mod
            while len(pw) <= k:
                pw.append(pw[-1] * base % mod)
                pwi.append(pwi[-1] * inv % mod)
        return pw, pwi

    def _moveToFront(self):  # the back half's first half becomes the front (the front is empty)
        k = (len(self.back) + 1) // 2
        moved = self.back[:k]
        self.back = self.back[k:]
        self.front = moved[::-1]

    def _moveToBack(self):  # the front half's last-stored half (its first values... no: its values nearest the middle) becomes the back
        k = (len(self.front) + 1) // 2
        moved = self.front[:k]  # (the values nearest the middle are stored first)
        self.front = self.front[k:]
        self.back = moved[::-1]
