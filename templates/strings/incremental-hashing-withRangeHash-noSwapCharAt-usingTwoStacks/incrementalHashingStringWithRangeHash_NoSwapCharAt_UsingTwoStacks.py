# DOES NOT HAVE swapCharAt(i, newChar) - cause this version is build with some 2 stacks thing
# we can add swapCharAt but I think it makes operations O(logN) something with a seg tree

import random

# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE
# hash convention: leftmost char is the highest power, i.e. "abc" -> a*base^2 + b*base + c
# Same surface as IncrementalHashing, but backed by two stacks so arbitrary ranges are queryable.
# The deque is split into a front half (stored reversed, suffix-anchored hashes) and a back half
# (stored in order, prefix-anchored hashes). A range lands in one half or straddles both.
# swapCharAt is NOT supported: a point update invalidates every prefix hash after it, which needs
# a Fenwick tree over ord(c)*base^(n-1-i) and would make every op O(log n).
#
# h = IncrementalHashing("abc")                     # uses all defaults (911 base, random mod)
# h = IncrementalHashing("abc", 131, 1000000007)    # your base and mod
# h.hashRange(l, r) -> int    hash of window[l..r] inclusive, 0-indexed, O(1)
# h.getHash() -> int          hash of the whole current window, O(1)
# h.hash(s) -> int            hash of an arbitrary string with these base/mod, O(len(s))
# h.addChar(c) -> None        append c on the right, O(1)
# h.popChar() -> None         drop the rightmost char, amortized O(1)
# h.addCharLeft(c) -> None    prepend c on the left, O(1)
# h.popCharLeft() -> None     drop the leftmost char, amortized O(1)
# h.slideRight(c) -> None     popCharLeft + addChar, amortized O(1)
# h.slideLeft(c) -> None      popChar + addCharLeft, amortized O(1)
# h.rotateRight() -> None     ABC -> CAB, amortized O(1)
# h.rotateLeft() -> None      ABC -> BCA, amortized O(1)
# h.charAt(i) -> str          char at index i, O(1)
# h.getCurrentWindow() -> str the current window as a string, O(n)
# h.length() -> int           current window length, O(1)
class IncrementalHashing:
    GOOD_MODS = [1000000007, 1000000009, 1000000021, 1000000033,
            1000000087, 1000000093, 1000000097, 1000000103,
            1000000123, 1000000181, 1000000207, 1000000223,
            1000000241, 1000000271, 1000000289, 1000000297]

    # O(n) time
    # Base is ideally prime and coprime to mod (needed so baseInv exists).
    def __init__(self, string: str, base: int = 911, mod: int = None):
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.baseInv = pow(base, -1, self.mod)
        self.basePow = [1]      # base^i % mod, grown lazily
        self.baseInvPow = [1]   # baseInv^i % mod, needed to shift a front-half range down to power 0
        self.front = []         # leftmost chars, REVERSED: front[0] is the char nearest the middle
        self.frontHashes = [0]  # frontHashes[j] = hash of the last j chars of the front half
        self.back = []          # rightmost chars, in order
        self.backHashes = [0]   # backHashes[j] = hash of the first j chars of the back half
        for c in string:
            self.addChar(c)

    # Grows both power tables until index `upTo` exists
    # amortized O(1)
    def _ensureBasePow(self, upTo: int):
        bp = self.basePow; base = self.base; mod = self.mod
        while len(bp) <= upTo:
            bp.append((bp[-1] * base) % mod)
        ip = self.baseInvPow; binv = self.baseInv
        while len(ip) <= upTo:
            ip.append((ip[-1] * binv) % mod)

    # Splits the window in half and rebuilds both stacks, called when the side we need is empty
    # O(n) but amortized O(1) across a sequence of ops
    def _rebalance(self, needFront: bool):
        window = self.getCurrentWindow()
        n = len(window)
        if n == 0:
            return
        mid = (n + 1) // 2 if needFront else n // 2
        mid = max(1, mid) if needFront else min(n - 1, mid)
        self.front = []; self.frontHashes = [0]
        for c in reversed(window[:mid]):
            self.addCharLeft(c)
        self.back = []; self.backHashes = [0]
        for c in window[mid:]:
            self.addChar(c)

    ################ PUBLIC METHODS START HERE ################

    # Hash of an arbitrary string with these base/mod (e.g. the pattern to match against)
    # O(len) time
    def hash(self, string: str) -> int:
        res = 0; base = self.base; mod = self.mod
        for c in string:
            res = (res * base + ord(c)) % mod
        return res

    # Appends a char on the right
    # O(1) time
    def addChar(self, c: str):
        self.back.append(c)
        self.backHashes.append((self.backHashes[-1] * self.base + ord(c)) % self.mod)

    # Prepends a char on the left
    # amortized O(1) time
    def addCharLeft(self, c: str):
        power = len(self.front)
        self._ensureBasePow(power)
        self.front.append(c)
        self.frontHashes.append((ord(c) * self.basePow[power] + self.frontHashes[-1]) % self.mod)

    # Removes the rightmost char
    # amortized O(1) time
    def popChar(self):
        if not self.back:
            self._rebalance(needFront=False)
        if self.back:
            self.back.pop()
            self.backHashes.pop()

    # Removes the leftmost char
    # amortized O(1) time
    def popCharLeft(self):
        if not self.front:
            self._rebalance(needFront=True)
        if self.front:
            self.front.pop()
            self.frontHashes.pop()

    # Slides a fixed-size window right: drop leftmost, add c on the right
    # amortized O(1) time
    def slideRight(self, c: str):
        self.popCharLeft()
        self.addChar(c)

    # Slides a fixed-size window left: drop rightmost, add c on the left
    # amortized O(1) time
    def slideLeft(self, c: str):
        self.popChar()
        self.addCharLeft(c)

    # Moves rightmost letter to front, like ABC -> CAB
    # amortized O(1) time
    def rotateRight(self):
        if self.length() < 2:
            return
        c = self.charAt(self.length() - 1)
        self.popChar()
        self.addCharLeft(c)

    # Moves leftmost letter to the end, like ABC -> BCA
    # amortized O(1) time
    def rotateLeft(self):
        if self.length() < 2:
            return
        c = self.charAt(0)
        self.popCharLeft()
        self.addChar(c)

    # Hash of window[l..r], inclusive, 0-indexed over the logical window
    # O(1) time
    def hashRange(self, l: int, r: int) -> int:
        if l > r:
            return 0
        mod = self.mod
        f = len(self.front)
        if r < f:
            # frontHashes[f-l] is the suffix from l, frontHashes[f-1-r] is the suffix from r+1,
            # so the difference is window[l..r] shifted up by base^(f-1-r); divide it back down
            self._ensureBasePow(f - 1 - r)
            return (self.frontHashes[f - l] - self.frontHashes[f - 1 - r]) * self.baseInvPow[f - 1 - r] % mod
        if l >= f:
            a = l - f; b = r - f
            self._ensureBasePow(b + 1 - a)
            return (self.backHashes[b + 1] - self.backHashes[a] * self.basePow[b + 1 - a]) % mod
        self._ensureBasePow(r - f + 1)
        left = self.hashRange(l, f - 1)
        right = self.hashRange(f, r)
        return (left * self.basePow[r - f + 1] + right) % mod

    # Hash of the whole current window
    # O(1) time
    def getHash(self) -> int:
        return self.hashRange(0, self.length() - 1)

    # Char at a logical index
    # O(1) time
    def charAt(self, index: int) -> str:
        f = len(self.front)
        return self.front[f - 1 - index] if index < f else self.back[index - f]

    # Returns the current window as a string
    # O(n) time
    def getCurrentWindow(self) -> str:
        return ''.join(reversed(self.front)) + ''.join(self.back)

    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return len(self.front) + len(self.back)
