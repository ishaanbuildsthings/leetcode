import random

# Palindrome hashing over an integer array via prefix + reversed-prefix rolling hashes.

# assumes values are in 0...1e9 range
# all mods in GOOD_MODS are > 1e9 to prevent some collisions
# base=911 is default

# for values >1e9 or negatives, give a mod bigger than the value range, compress values, or maybe shift values with negatives

# h = PalindromeHashing([1, 2, 3, 2, 1])                    # uses all defaults
# h = PalindromeHashing(arr, 131)                           # your base, default mod
# h = PalindromeHashing(arr, 131, 1000000007)               # your base and mod


# h.isPalindrome(l, r) -> bool
# h.getHashForSubstring(l, r) -> int
# h.getHashForReversedSubstring(l, r) -> int
# h.addChar(v) -> None     appends a value to the end, but breaks palindromic work(?) since reverse hashes are not maintained
# h.popChar() -> None      pops the last value, breaks palindromic work(?) since reverse hashes are not maintained
# h.getHash() -> int        the overall hash
# h.getCurrentWindow() -> list     just returns the current array O(n) as we return by value
# h.length() -> int         how long is our window
# h.longestPalindromeCenteredAroundI(i) -> (int, int) gives us L and R for the longest centered around i, O(logN)
# h.longestPalindromeCenteredAroundIAndIPlusOne(i) -> (int, int) gives us L and R for the longest centered around [i...i+1] or (i+1,i) if invalid center, O(logN)


class PalindromeHashing:
    # List of good prime numbers for hashing, will choose randomly if not provided
    GOOD_MODS = [1000000007, 1000000009, 1000000021, 1000000033,
            1000000087, 1000000093, 1000000097, 1000000103,
            1000000123, 1000000181, 1000000207, 1000000223,
            1000000241, 1000000271, 1000000289, 1000000297]

    # O(n) time
    # Assumes values in [0, 1e9]; every mod above is > 1e9 so raw values are safe (mod > max value keeps distinct values distinct).
    # Base is ideally prime and coprime to mod; base size doesn't affect correctness once mod > max value.
    def __init__(self, arr, base: int = 911, mod: int = None):
        self.window = list(arr)
        self.n = len(arr)
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.prefixHashes = self._buildPrefixHashes(arr) # O(n) time
        self.reversePrefixHashes = self._buildReversePrefixHashes(arr) # O(n) time
        self.basePow = self._precomputeBasePowers(len(arr)) # O(n) time

    # Gets the hash of a subarray [left...right] using math
    # O(1) time
    def getHashForSubstring(self, left: int, right: int) -> int:
        return (self.prefixHashes[right + 1] - self.prefixHashes[left] * self.basePow[right - left + 1]) % self.mod

    # Gets the hash of a reversed section of the array, uses the original array indices
    # O(1) time
    def getHashForReversedSubstring(self, originalStringLeft: int, originalStringRight: int) -> int:
        left = self.n - originalStringRight - 1
        right = self.n - originalStringLeft
        return (self.reversePrefixHashes[right] - self.reversePrefixHashes[left] * self.basePow[right - left]) % self.mod

    # O(1) time
    def isPalindrome(self, left: int, right: int) -> bool:
        return self.getHashForSubstring(left, right) == self.getHashForReversedSubstring(left, right)

    # Longest odd-length palindrome centered at i. Returns inclusive (l, r) (always valid, >= (i, i)).
    # O(log n) time. Hash test inlined + arrays hoisted to locals for speed.
    def longestPalindromeCenteredAroundI(self, i: int) -> tuple:
        n = self.n; mod = self.mod
        p = self.prefixHashes; rp = self.reversePrefixHashes; bp = self.basePow
        lo, hi, best = 1, min(i + 1, n - i), 1 # best = radius (values on each side incl. center)
        while lo <= hi:
            m = (lo + hi) // 2
            l = i - m + 1; r = i + m - 1
            fwd = (p[r + 1] - p[l] * bp[r - l + 1]) % mod
            rl = n - r - 1; rr = n - l
            rev = (rp[rr] - rp[rl] * bp[rr - rl]) % mod
            if fwd == rev:
                best = m
                lo = m + 1
            else:
                hi = m - 1
        return (i - best + 1, i + best - 1)

    # Longest even-length palindrome centered between i and i+1. Returns inclusive (l, r),
    # or an empty range (l > r, i.e. (i+1, i)) if arr[i] != arr[i+1].
    # O(log n) time. Hash test inlined + arrays hoisted to locals for speed.
    def longestPalindromeCenteredAroundIAndIPlusOne(self, i: int) -> tuple:
        n = self.n; mod = self.mod
        window = self.window
        if i + 1 >= n or window[i] != window[i + 1]: # O(1) short-circuit: no even palindrome here, skip the search
            return (i + 1, i)
        p = self.prefixHashes; rp = self.reversePrefixHashes; bp = self.basePow
        lo, hi, best = 1, min(i + 1, n - i - 1), 0 # best = radius (values on each side of the gap)
        while lo <= hi:
            m = (lo + hi) // 2
            l = i - m + 1; r = i + m
            fwd = (p[r + 1] - p[l] * bp[r - l + 1]) % mod
            rl = n - r - 1; rr = n - l
            rev = (rp[rr] - rp[rl] * bp[rr - rl]) % mod
            if fwd == rev:
                best = m
                lo = m + 1
            else:
                hi = m - 1
        return (i - best + 1, i + best)

    # Adds a value to the end of the array and updates hashes
    # O(1) time
    def addChar(self, v):
        self.window.append(v)
        self.n += 1
        if self.n > len(self.basePow):
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)
        self.prefixHashes.append((self.prefixHashes[-1] * self.base + v) % self.mod)
        self.reversePrefixHashes.append((self.reversePrefixHashes[-1] * self.base + v) % self.mod)

    # Removes the last value from the array and updates hashes
    # O(1) time
    def popChar(self):
        if self.n == 0:
            return
        self.window.pop()
        self.n -= 1
        self.prefixHashes.pop()
        self.reversePrefixHashes.pop()

    # Gets the hash of the entire window
    # O(1) time
    def getHash(self) -> int:
        return self.prefixHashes[-1]

    # Returns the current window
    # O(n) time (copies the array)
    def getCurrentWindow(self) -> list:
        return list(self.window)

    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return self.n

    # Builds the prefix hashes of the array, prefixHashes[i] is for arr[:i], so prefixHashes[0] is for the empty array
    # O(n) time
    def _buildPrefixHashes(self, arr):
        prefixHashes = [0] * (len(arr) + 1)
        for i in range(1, len(arr) + 1):
            prefixHashes[i] = (prefixHashes[i - 1] * self.base + arr[i - 1]) % self.mod
        return prefixHashes

    # Builds the prefix hashes of the reversed array, so reversedPrefixHashes[2] is the hash of the first two element prefix, but that prefix is reversed. reversedPrefixHashes[0] is for the empty array
    # arr = [a, b, c], reverse prefixes are [a], [b, a], [c, b, a]
    # O(n) time
    def _buildReversePrefixHashes(self, arr):
        reversePrefixHashes = [0] * (len(arr) + 1)
        for i in range(1, len(arr) + 1):
            reversePrefixHashes[i] = (reversePrefixHashes[i - 1] * self.base + arr[-i]) % self.mod
        return reversePrefixHashes

    # Precompute powers of base, so base^0 % MOD, base^1 % MOD, base^2 % MOD, ...
    # O(n) time
    def _precomputeBasePowers(self, length: int):
        basePow = [1] * (length + 1)
        for i in range(1, length + 1):
            basePow[i] = (basePow[i - 1] * self.base) % self.mod
        return basePow