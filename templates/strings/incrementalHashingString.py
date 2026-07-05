import random
from collections import deque

# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE
# hash convention: leftmost char is the highest power, i.e. "abc" -> a*base^2 + b*base + c

# h = IncrementalHashing("abc")                     # uses all defaults (911 base, random mod)
# h = IncrementalHashing("abc", 131)                # your base, default random mod
# h = IncrementalHashing("abc", 131, 1000000007)    # your base and mod


# h.getHash() -> int          hash of the whole current window, O(1)
# h.hash(s) -> int            hash of an arbitrary string with these base/mod (for comparisons), O(len(s))
# h.addChar(c) -> None        append c on the right, O(1)
# h.popChar() -> None         drop the rightmost char, O(1)
# h.addCharLeft(c) -> None    prepend c on the left, O(1)
# h.popCharLeft() -> None     drop the leftmost char, O(1)
# h.slideRight(c) -> None     popCharLeft + addChar (slide a fixed window right), O(1)
# h.slideLeft(c) -> None      popChar + addCharLeft (slide a fixed window left), O(1)

# NOTE THIS IS O(i) NOT O(1) BECAUSE PYTHON DEQUE DOES NOT HAVE O(1) ACCESS, WE WOULD NEED A CUSTOM DEQUE TO FIX THAT
# h.swapCharAt(i, c) -> None  replace char at index i, O(i) for the deque index + O(1) hash update
# h.getCurrentWindow() -> str the current window as a string, O(n)
# h.length() -> int           current window length, O(1)


class IncrementalHashing:
    # List of good prime numbers for hashing, will choose randomly if not provided
    GOOD_MODS = [1000000007, 1000000009, 1000000021, 1000000033,
            1000000087, 1000000093, 1000000097, 1000000103,
            1000000123, 1000000181, 1000000207, 1000000223,
            1000000241, 1000000271, 1000000289, 1000000297]

    # O(n) time
    # Base is ideally prime and coprime to mod (needed so baseInv exists); base size doesn't affect correctness once mod > max char value (mods here are >1e9, chars are ord() so always safe).
    def __init__(self, string: str, base: int = 911, mod: int = None):
        self.window = deque(string)
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.baseInv = pow(base, -1, self.mod)  # for popChar (divide out the rightmost char)
        self.basePow = [1]  # base^0 % mod, grown lazily
        self.hashValue = 0
        for c in self.window:
            self.hashValue = (self.hashValue * base + ord(c)) % self.mod
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

    # Hash of an arbitrary string with these base/mod (e.g. the pattern to match against)
    # O(len) time
    def hash(self, string: str) -> int:
        res = 0; base = self.base; mod = self.mod
        for c in string:
            res = (res * base + ord(c)) % mod
        return res

    # Appends a char on the right and updates the hash
    # O(1) time
    def addChar(self, c: str):
        self.window.append(c)
        self.hashValue = (self.hashValue * self.base + ord(c)) % self.mod
        if len(self.basePow) <= len(self.window):   # keep basePow one ahead of the window
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)

    # Removes the rightmost char and updates the hash
    # O(1) time
    def popChar(self):
        if not self.window:
            return
        c = self.window.pop()
        self.hashValue = (self.hashValue - ord(c)) * self.baseInv % self.mod

    # Prepends a char on the left and updates the hash
    # O(1) time
    def addCharLeft(self, c: str):
        self.window.appendleft(c)
        k = len(self.window) - 1  # power of the new leftmost char = old length
        self.hashValue = (ord(c) * self.basePow[k] + self.hashValue) % self.mod
        if len(self.basePow) <= len(self.window):   # keep basePow one ahead of the window
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)

    # Removes the leftmost char and updates the hash
    # O(1) time
    def popCharLeft(self):
        if not self.window:
            return
        c = self.window.popleft()
        self.hashValue = (self.hashValue - ord(c) * self.basePow[len(self.window)]) % self.mod

    # Slides a fixed-size window right: drop leftmost, add c on the right
    # O(1) time. Inlined (window size is constant so basePow never grows here).
    def slideRight(self, c: str):
        w = self.window
        mod = self.mod
        left = w.popleft()
        hv = (self.hashValue - ord(left) * self.basePow[len(w)]) % mod
        w.append(c)
        self.hashValue = (hv * self.base + ord(c)) % mod

    # Slides a fixed-size window left: drop rightmost, add c on the left
    # O(1) time. Inlined (window size is constant so basePow never grows here).
    def slideLeft(self, c: str):
        w = self.window
        mod = self.mod
        right = w.pop()
        hv = (self.hashValue - ord(right)) * self.baseInv % mod
        w.appendleft(c)
        self.hashValue = (ord(c) * self.basePow[len(w) - 1] + hv) % mod

    # Replaces the char at index and updates the hash
    # NOTE THIS IS O(i) NOT O(1) BECAUSE PYTHON DEQUE DOES NOT HAVE O(1) ACCESS, WE WOULD NEED A CUSTOM DEQUE TO FIX THAT
    def swapCharAt(self, index: int, newChar: str):
        if index < 0 or index >= len(self.window):
            raise IndexError("Index out of range")
        power = len(self.window) - 1 - index
        oldChar = self.window[index]
        self.window[index] = newChar
        self.hashValue = (self.hashValue + (ord(newChar) - ord(oldChar)) * self.basePow[power]) % self.mod

    # Returns the current window as a string
    # O(n) time (joins into a string)
    def getCurrentWindow(self) -> str:
        return ''.join(self.window)

    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return len(self.window)