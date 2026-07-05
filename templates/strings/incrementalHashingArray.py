import random
from collections import deque

# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

# assumes values are in 0...1e9 range; all mods in GOOD_MODS are > 1e9 to prevent value collisions; base=911 default
# for values >1e9 or negatives, give a mod bigger than the value range, compress values, or shift negatives up


# h = IncrementalHashing([1, 2, 3])                 # uses all defaults (911 base, random mod)
# h = IncrementalHashing(arr, 131)                  # your base, default random mod
# h = IncrementalHashing(arr, 131, 1000000007)      # your base and mod


# h.getHash() -> int          hash of the whole current window, O(1)
# h.hash(a) -> int            hash of an arbitrary array with these base/mod (for comparisons), O(len(a))
# h.addChar(v) -> None        append v on the right, O(1)
# h.popChar() -> None         drop the rightmost value, O(1)
# h.addCharLeft(v) -> None    prepend v on the left, O(1)
# h.popCharLeft() -> None     drop the leftmost value, O(1)
# h.slideRight(v) -> None     popCharLeft + addChar (slide a fixed window right), O(1)
# h.slideLeft(v) -> None      popChar + addCharLeft (slide a fixed window left), O(1)

# NOTE THIS IS O(i) NOT O(1) BECAUSE PYTHON DEQUE DOES NOT HAVE O(1) ACCESS, WE WOULD NEED A CUSTOM DEQUE TO FIX THAT
# h.swapCharAt(i, v) -> None  replace value at index i, O(i) for the deque index + O(1) hash update
# h.getCurrentWindow() -> list  the current window as a list, O(n)
# h.length() -> int           current window length, O(1)


class IncrementalHashing:
    # List of good prime numbers for hashing, will choose randomly if not provided
    GOOD_MODS = [1000000007, 1000000009, 1000000021, 1000000033,
            1000000087, 1000000093, 1000000097, 1000000103,
            1000000123, 1000000181, 1000000207, 1000000223,
            1000000241, 1000000271, 1000000289, 1000000297]

    # O(n) time
    # Assumes values in [0, 1e9]; every mod above is > 1e9 so raw values are safe (mod > max value keeps distinct values distinct).
    # Base is ideally prime and coprime to mod (needed so baseInv exists); base size doesn't affect correctness once mod > max value.
    def __init__(self, arr, base: int = 911, mod: int = None):
        self.window = deque(arr)
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.baseInv = pow(base, -1, self.mod)  # for popChar (divide out the rightmost value)
        self.basePow = [1]  # base^0 % mod, grown lazily
        self.hashValue = 0
        for v in self.window:
            self.hashValue = (self.hashValue * base + v) % self.mod
        self._ensureBasePow(len(self.window))

    # Grows basePow until index `upTo` exists
    # amortized O(1)
    def _ensureBasePow(self, upTo: int):
        bp = self.basePow; base = self.base; mod = self.mod
        while len(bp) <= upTo:
            bp.append((bp[-1] * base) % mod)

    # Hash of the whole current window
    # O(1) time
    def getHash(self) -> int:
        return self.hashValue

    # Hash of an arbitrary array with these base/mod (e.g. the pattern to match against)
    # O(len) time
    def hash(self, arr) -> int:
        res = 0; base = self.base; mod = self.mod
        for v in arr:
            res = (res * base + v) % mod
        return res

    # Appends a value on the right and updates the hash
    # O(1) time
    def addChar(self, v):
        self.window.append(v)
        self.hashValue = (self.hashValue * self.base + v) % self.mod
        if len(self.basePow) <= len(self.window):   # keep basePow one ahead of the window
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)

    # Removes the rightmost value and updates the hash
    # O(1) time
    def popChar(self):
        if not self.window:
            return
        v = self.window.pop()
        self.hashValue = (self.hashValue - v) * self.baseInv % self.mod

    # Prepends a value on the left and updates the hash
    # O(1) time
    def addCharLeft(self, v):
        self.window.appendleft(v)
        k = len(self.window) - 1  # power of the new leftmost value = old length
        self.hashValue = (v * self.basePow[k] + self.hashValue) % self.mod
        if len(self.basePow) <= len(self.window):   # keep basePow one ahead of the window
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)

    # Removes the leftmost value and updates the hash
    # O(1) time
    def popCharLeft(self):
        if not self.window:
            return
        v = self.window.popleft()
        self.hashValue = (self.hashValue - v * self.basePow[len(self.window)]) % self.mod

    # Slides a fixed-size window right: drop leftmost, add v on the right
    # O(1) time. Inlined (window size is constant so basePow never grows here).
    def slideRight(self, v):
        w = self.window
        mod = self.mod
        left = w.popleft()
        hv = (self.hashValue - left * self.basePow[len(w)]) % mod
        w.append(v)
        self.hashValue = (hv * self.base + v) % mod

    # Slides a fixed-size window left: drop rightmost, add v on the left
    # O(1) time. Inlined (window size is constant so basePow never grows here).
    def slideLeft(self, v):
        w = self.window
        mod = self.mod
        right = w.pop()
        hv = (self.hashValue - right) * self.baseInv % mod
        w.appendleft(v)
        self.hashValue = (v * self.basePow[len(w) - 1] + hv) % mod

    # Replaces the value at index and updates the hash
    # NOTE THIS IS O(i) NOT O(1) BECAUSE PYTHON DEQUE DOES NOT HAVE O(1) ACCESS, WE WOULD NEED A CUSTOM DEQUE TO FIX THAT
    def swapCharAt(self, index: int, newVal):
        if index < 0 or index >= len(self.window):
            raise IndexError("Index out of range")
        power = len(self.window) - 1 - index
        oldVal = self.window[index]
        self.window[index] = newVal
        self.hashValue = (self.hashValue + (newVal - oldVal) * self.basePow[power]) % self.mod

    # Returns the current window as a list
    # O(n) time (copies into a list)
    def getCurrentWindow(self) -> list:
        return list(self.window)

    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return len(self.window)