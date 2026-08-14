# This seg tree can basically add and pop from both left and right, swap chars at random positions, and get range hashes
# This is the WITH-PALINDROME variant: every node also stores the hash of its range REVERSED, which
# costs one more array and one more line per update. That buys isPalindrome / hashRangeReversed /
# isReverseOf. If you never need those, use the NoPalindrome file, it is meaningfully faster
# it works by creating a seg tree bigger than normal, giving padding on the left and right to "slide around in" and we maintain pointers
# most operations logN, some like popping are just O(1) since we literally just move a pointer, but if we add a char we actually need to point set
# If we don't want swapCharAt then we can use the two-stacks as a deque pour/fill trick and get O(1) everything WITH range hashing

import random

# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE
# hash convention: leftmost char is the highest power, i.e. "abc" -> a*base^2 + b*base + c
# Backed by an iterative bottom-up segment tree over a fixed buffer, with two cursors marking the
# live window inside it. An unused slot holds the value 0 and still occupies its slot, so every
# node's width is just its subtree size - that makes the merge shift a per-level constant
# (levelPow) and means no per-node length has to be stored. Padding zeros can never pollute an
# answer because hashRange only accumulates nodes lying entirely inside [left, right).
# The merge is NOT commutative, so hashRange accumulates its left-side and right-side pieces
# separately and joins them at the end.
# The reverse hash mirrors the forward one: for a node with children A (left) and B (right),
# forward is A then B, reversed is reverse(B) then reverse(A), so the shift lands on the other
# child. Same idea in hashRangeReversed - appending a node on the left of the forward range means
# prepending its reverse on the right of the reversed range.
# Unlike the 2-stacks version this DOES support swapCharAt, at the cost of O(log n) instead of
# O(1). Still ~4x slower than the 2-stacks version, so only reach for this when you actually
# need swapCharAt.
# maxLeftGrowth / maxRightGrowth are how many chars you will ever add past each end of `string`.
# They are required and they are HARD LIMITS: exceeding one raises. There is no auto-grow, so
# every op is a true O(log n) with no hidden rebuild, and the buffer never balloons.
# Note popCharLeft does NOT give the space back - a window slid right n times consumes n slots of
# right growth, so size maxRightGrowth for total slides, not for the live window length.
# Popping is O(1): it only moves a cursor and leaves the leaf stale. Safe for the same reason the
# padding is safe - a node holding a dead slot is never read, and addChar overwrites the leaf
# before it can be. The consequence is that self.chars holds garbage outside [left, right), so
# always slice by the cursors.
# Capacity is rounded up to a power of two, which gives leaves at cap+i and a 2*cap node array.

# h = RangeHashingSeg("abc", 0, 100)                      # never prepend, append up to 100 chars
# h = RangeHashingSeg("", n, n)                           # build either direction, up to n each
# h = RangeHashingSeg("abc", 0, 100, 131, 1000000007)     # your base and mod

# h.hashRange(l, r) -> int    hash of window[l..r] inclusive, 0-indexed, O(log n)
# h.hashRangeReversed(l, r) -> int  hash of window[l..r] read backwards, O(log n)
# h.isPalindrome(l, r) -> bool      is window[l..r] a palindrome, O(log n)
# h.rangesEqual(l1,r1,l2,r2) -> bool    do the two ranges hold the same string, O(log n)
# h.isReverseOf(l1,r1,l2,r2) -> bool    is the first range the reverse of the second, O(log n)
# h.isPalindromeConcat(l1,r1,l2,r2) -> bool  is window[l1..r1] + window[l2..r2] a palindrome, O(log n)
# h.longestPalCenteredAroundI(i) -> int      length of the longest odd palindrome centred on i, O(log^2 n)
# h.longestPalCenteredAroundII(i) -> int     length of the longest even palindrome centred between i and i+1, O(log^2 n)
# h.getHash() -> int          hash of the whole current window, O(log n)
# h.hash(s) -> int            hash of an arbitrary string with these base/mod, O(len(s))
# h.addChar(c) -> None        append c on the right, O(log n)
# h.popChar() -> None         drop the rightmost char, O(1)
# h.popChars(cnt) -> None     drop the last cnt chars, O(1)
# h.addCharLeft(c) -> None    prepend c on the left, O(log n)
# h.popCharLeft() -> None     drop the leftmost char, O(1)
# h.popCharsLeft(cnt) -> None drop the first cnt chars, O(1)
# h.slideRight(c) -> None     popCharLeft + addChar, O(log n)
# h.slideLeft(c) -> None      popChar + addCharLeft, O(log n)
# h.rotateRight() -> None     ABC -> CAB, O(log n)
# h.rotateLeft() -> None      ABC -> BCA, O(log n)
# h.swapCharAt(i, c) -> None  replace char at index i, O(log n)
# h.charAt(i) -> str          char at index i, O(1)
# h.getCurrentWindow() -> str the current window as a string, O(n)
# h.length() -> int           current window length, O(1)


class RangeHashingSeg:
    # List of good prime numbers for hashing, will choose randomly if not provided
    GOOD_MODS = [1000000007, 1000000009, 1000000021, 1000000033,
            1000000087, 1000000093, 1000000097, 1000000103,
            1000000123, 1000000181, 1000000207, 1000000223,
            1000000241, 1000000271, 1000000289, 1000000297]

    # O(capacity) time
    # Base is ideally prime and coprime to mod; mod > max char value keeps distinct chars distinct.
    def __init__(self, string: str, maxLeftGrowth: int, maxRightGrowth: int,
                 base: int = 911, mod: int = None):
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.basePow = [1]
        self._allocate(maxLeftGrowth, string, maxRightGrowth)

    # Lays out `string` with the requested slack on each side, rounds capacity up to a power of
    # two (leaves live at cap+i, so the node array is 2*cap), and builds level by level
    # O(capacity) time
    def _allocate(self, leftSlack: int, string: str, rightSlack: int):
        need = leftSlack + len(string) + rightSlack
        cap = 1
        while cap < max(2, need):
            cap *= 2
        self.cap = cap
        self.chars = [None] * cap
        self.hashes = [0] * (2 * cap)
        self.revHashes = [0] * (2 * cap)
        self.left = leftSlack
        self.right = self.left + len(string)
        self._ensureBasePow(cap)
        # levelPow[h] = base^(2^h): the shift for merging two children of height h
        lp = []
        h = 0
        while (1 << h) <= cap:
            lp.append(self.basePow[1 << h])
            h += 1
        self.levelPow = lp
        H = self.hashes; R = self.revHashes; mod = self.mod
        for i, c in enumerate(string):
            self.chars[self.left + i] = c
            H[cap + self.left + i] = ord(c)
            R[cap + self.left + i] = ord(c)
        lo = cap >> 1
        h = 0
        while lo >= 1:
            for i in range(lo, lo << 1):
                H[i] = (H[2*i] * lp[h] + H[2*i+1]) % mod
                R[i] = (R[2*i+1] * lp[h] + R[2*i]) % mod
            h += 1
            lo >>= 1

    # Grows basePow until index `upTo` exists
    # amortized O(1)
    def _ensureBasePow(self, upTo: int):
        bp = self.basePow; base = self.base; mod = self.mod
        while len(bp) <= upTo:
            bp.append((bp[-1] * base) % mod)

    # Writes one leaf and walks up recomputing parents; None means an empty slot, stored as 0
    # O(log n) time
    def _pointSet(self, pos: int, c):
        self.chars[pos] = c
        H = self.hashes; R = self.revHashes; lp = self.levelPow; mod = self.mod
        i = self.cap + pos
        v = 0 if c is None else ord(c)
        H[i] = v
        R[i] = v
        i >>= 1
        h = 0
        while i:
            j = i << 1
            H[i] = (H[j] * lp[h] + H[j+1]) % mod
            R[i] = (R[j+1] * lp[h] + R[j]) % mod
            h += 1
            i >>= 1

    ################ PUBLIC METHODS START HERE ################

    # Hash of an arbitrary string with these base/mod (e.g. the pattern to match against)
    # O(len) time
    def hash(self, string: str) -> int:
        res = 0; base = self.base; mod = self.mod
        for c in string:
            res = (res * base + ord(c)) % mod
        return res

    # Appends a char on the right
    # O(log n) time
    def addChar(self, c: str):
        if self.right == self.cap:
            raise IndexError("out of right growth, raise maxRightGrowth")
        self._pointSet(self.right, c)
        self.right += 1

    # Prepends a char on the left
    # O(log n) time
    def addCharLeft(self, c: str):
        if self.left == 0:
            raise IndexError("out of left growth, raise maxLeftGrowth")
        self.left -= 1
        self._pointSet(self.left, c)

    # Removes the rightmost char. Just moves the cursor - the leaf is left stale on purpose, see
    # the note at the top of the file
    # O(1) time
    def popChar(self):
        if self.right == self.left:
            return
        self.right -= 1

    # Removes the leftmost char. Just moves the cursor, same as popChar
    # O(1) time
    def popCharLeft(self):
        if self.right == self.left:
            return
        self.left += 1

    # Removes the last `count` chars in one cursor move, clamped at empty
    # O(1) time
    def popChars(self, count: int):
        if count >= self.right - self.left:
            self.right = self.left
        else:
            self.right -= count

    # Removes the first `count` chars in one cursor move, clamped at empty
    # O(1) time
    def popCharsLeft(self, count: int):
        if count >= self.right - self.left:
            self.left = self.right
        else:
            self.left += count

    # Slides a fixed-size window right: drop leftmost, add c on the right
    # O(log n) time
    def slideRight(self, c: str):
        self.popCharLeft()
        self.addChar(c)

    # Slides a fixed-size window left: drop rightmost, add c on the left
    # O(log n) time
    def slideLeft(self, c: str):
        self.popChar()
        self.addCharLeft(c)

    # moves rightmost letter to front, like ABC -> CAB
    # O(log n) time
    def rotateRight(self):
        if self.length() < 2:
            return
        c = self.chars[self.right - 1]
        self.popChar()
        self.addCharLeft(c)

    # moves leftmost letter to the end, like ABC -> BCA
    # O(log n) time
    def rotateLeft(self):
        if self.length() < 2:
            return
        c = self.chars[self.left]
        self.popCharLeft()
        self.addChar(c)

    # Replaces the char at a logical index
    # O(log n) time
    def swapCharAt(self, index: int, newChar: str):
        if index < 0 or index >= self.length():
            raise IndexError("Index out of range")
        self._pointSet(self.left + index, newChar)

    # Hash of window[l..r], inclusive, 0-indexed over the logical window
    # Nodes picked up on the left get appended to the left accumulator, nodes picked up on the
    # right get prepended to the right accumulator; the merge is not commutative so the two
    # sides are kept apart until the final join. Node widths come from the level counter h
    # O(log n) time
    def hashRange(self, l: int, r: int) -> int:
        if l > r:
            return 0
        H = self.hashes; bp = self.basePow; lp = self.levelPow; mod = self.mod; cap = self.cap
        lo = cap + self.left + l
        hi = cap + self.left + r + 1
        lh = 0; rh = 0; rlen = 0
        h = 0
        while lo < hi:
            if lo & 1:
                lh = (lh * lp[h] + H[lo]) % mod
                lo += 1
            if hi & 1:
                hi -= 1
                rh = (H[hi] * bp[rlen] + rh) % mod
                rlen += 1 << h
            lo >>= 1; hi >>= 1; h += 1
        return (lh * bp[rlen] + rh) % mod

    # Hash of window[l..r] read backwards, i.e. the hash of reverse(window[l..r])
    # Appending a node on the left of the forward range is prepending its reverse on the right of
    # the reversed range, so the two accumulators swap roles compared to hashRange
    # O(log n) time
    def hashRangeReversed(self, l: int, r: int) -> int:
        if l > r:
            return 0
        R = self.revHashes; bp = self.basePow; mod = self.mod; cap = self.cap
        lo = cap + self.left + l
        hi = cap + self.left + r + 1
        lrev = 0; llen = 0
        rrev = 0
        h = 0
        while lo < hi:
            w = 1 << h
            if lo & 1:
                lrev = (R[lo] * bp[llen] + lrev) % mod
                llen += w
                lo += 1
            if hi & 1:
                hi -= 1
                rrev = (rrev * bp[w] + R[hi]) % mod
            lo >>= 1; hi >>= 1; h += 1
        return (rrev * bp[llen] + lrev) % mod

    # Is window[l..r] a palindrome
    # O(log n) time
    def isPalindrome(self, l: int, r: int) -> bool:
        return self.hashRange(l, r) == self.hashRangeReversed(l, r)

    # Do the two ranges hold the same string
    # O(log n) time
    def rangesEqual(self, l1: int, r1: int, l2: int, r2: int) -> bool:
        if r1 - l1 != r2 - l2:
            return False
        return self.hashRange(l1, r1) == self.hashRange(l2, r2)

    # Is the first range the reverse of the second
    # O(log n) time
    def isReverseOf(self, l1: int, r1: int, l2: int, r2: int) -> bool:
        if r1 - l1 != r2 - l2:
            return False
        return self.hashRange(l1, r1) == self.hashRangeReversed(l2, r2)

    # Is the concatenation window[l1..r1] + window[l2..r2] a palindrome, without materialising it.
    # Forward is piece1 then piece2, so piece1 shifts up by len2; reversed is reverse(piece2) then
    # reverse(piece1), so the reversed piece2 shifts up by len1. Either range may be empty (l > r)
    # O(log n) time
    def isPalindromeConcat(self, l1: int, r1: int, l2: int, r2: int) -> bool:
        bp = self.basePow; mod = self.mod
        len1 = r1 - l1 + 1 if r1 >= l1 else 0
        len2 = r2 - l2 + 1 if r2 >= l2 else 0
        self._ensureBasePow(max(len1, len2))
        fwd = (self.hashRange(l1, r1) * bp[len2] + self.hashRange(l2, r2)) % mod
        rev = (self.hashRangeReversed(l2, r2) * bp[len1] + self.hashRangeReversed(l1, r1)) % mod
        return fwd == rev

    # Length of the longest ODD-length palindrome centred on index i (always at least 1).
    # Binary searches the radius, which is valid because a centre that works at radius r also
    # works at every smaller radius
    # O(log^2 n) time
    def longestPalCenteredAroundI(self, i: int) -> int:
        n = self.length()
        lo = 0
        hi = min(i, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return 2 * lo + 1

    # Length of the longest EVEN-length palindrome centred between i and i+1, 0 if there is none
    # O(log^2 n) time
    def longestPalCenteredAroundII(self, i: int) -> int:
        n = self.length()
        if i + 1 >= n or self.charAt(i) != self.charAt(i + 1):
            return 0
        lo = 1
        hi = min(i + 1, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid + 1, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return 2 * lo

    # Hash of the whole current window
    # O(log n) time
    def getHash(self) -> int:
        if self.length() == 0:
            return 0
        return self.hashRange(0, self.length() - 1)

    # Char at a logical index
    # O(1) time
    def charAt(self, index: int) -> str:
        return self.chars[self.left + index]

    # Returns the current window as a string
    # O(n) time
    def getCurrentWindow(self) -> str:
        return ''.join(self.chars[self.left:self.right])

    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return self.right - self.left