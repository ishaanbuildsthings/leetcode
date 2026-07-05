import random

# Palindrome hashing over a string via prefix + reversed-prefix rolling hashes.

# Works out of the box for all ASCII strings uses base=911, random mod

# h = PalindromeHashing("abacaba")                    # uses all defaults
# h = PalindromeHashing("abacaba", 131)               # your base, default mod
# h = PalindromeHashing("abacaba", 131, 1000000007)   # your base and mod


# h.isPalindrome(l, r) -> bool
# h.getHashForSubstring(l, r) -> int
# h.getHashForReversedSubstring(l, r) -> int
# h.addChar(c) -> None     appends a char to the end, but breaks palindromic work(?) since reverse hashes are not maintained
# h.popChar() -> None      pops the last char, breaks palindromic work(?) since reverse hashes are not maintained
# h.getHash() -> int        the overall hash
# h.getCurrentWindow() -> str     just returns the current string O(n) as we return by value
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
    # Base is ideally prime and coprime to mod; base size doesn't affect correctness once mod > max char value (mods here are >1e9, chars are ord() so always safe).
    def __init__(self, string: str, base: int = 911, mod: int = None):
        self.window = list(string)
        self.n = len(string)
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.prefixHashes = self._buildPrefixHashes(string) # O(n) time
        self.reversePrefixHashes = self._buildReversePrefixHashes(string) # O(n) time
        self.basePow = self._precomputeBasePowers(len(string)) # O(n) time
 
    # Gets the hash of a substring [left...right] using math
    # O(1) time
    def getHashForSubstring(self, left: int, right: int) -> int:
        return (self.prefixHashes[right + 1] - self.prefixHashes[left] * self.basePow[right - left + 1]) % self.mod
 
    # Gets the hash of a reversed section of the string, uses the original string indices
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
        lo, hi, best = 1, min(i + 1, n - i), 1 # best = radius (chars on each side incl. center)
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
    # or an empty range (l > r, i.e. (i+1, i)) if s[i] != s[i+1].
    # O(log n) time. Hash test inlined + arrays hoisted to locals for speed.
    def longestPalindromeCenteredAroundIAndIPlusOne(self, i: int) -> tuple:
        n = self.n; mod = self.mod
        window = self.window
        if i + 1 >= n or window[i] != window[i + 1]: # O(1) short-circuit: no even palindrome here, skip the search
            return (i + 1, i)
        p = self.prefixHashes; rp = self.reversePrefixHashes; bp = self.basePow
        lo, hi, best = 1, min(i + 1, n - i - 1), 0 # best = radius (chars on each side of the gap)
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
 
    # Adds a character to the end of the string and updates hashes
    # O(1) time
    def addChar(self, c: str):
        self.window.append(c)
        self.n += 1
        if self.n > len(self.basePow):
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)
        self.prefixHashes.append((self.prefixHashes[-1] * self.base + ord(c)) % self.mod)
        self.reversePrefixHashes.append((self.reversePrefixHashes[-1] * self.base + ord(c)) % self.mod)
 
    # Removes the last character from the string and updates hashes
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
    # O(n) time (joins into a string)
    def getCurrentWindow(self) -> str:
        return ''.join(self.window)
 
    # Returns the length of the current window
    # O(1) time
    def length(self) -> int:
        return self.n
 
    # Builds the prefix hashes of the string, prefixHashes[i] is for string[:i], so prefixHashes[0] is for the empty string
    # O(n) time
    def _buildPrefixHashes(self, string: str):
        prefixHashes = [0] * (len(string) + 1)
        for i in range(1, len(string) + 1):
            prefixHashes[i] = (prefixHashes[i - 1] * self.base + ord(string[i - 1])) % self.mod
        return prefixHashes
 
    # Builds the prefix hashes of the reversed string, so reversedPrefixHashes[2] is the hash of the first two character prefix, but that prefix is reversed. reversedPrefixHashes[0] is for the empty string
    # string = 'abc', reverse prefixes are 'a', 'ba', 'cba'
    # O(n) time
    def _buildReversePrefixHashes(self, string: str):
        reversePrefixHashes = [0] * (len(string) + 1)
        for i in range(1, len(string) + 1):
            reversePrefixHashes[i] = (reversePrefixHashes[i - 1] * self.base + ord(string[-i])) % self.mod
        return reversePrefixHashes
 
    # Precompute powers of base, so base^0 % MOD, base^1 % MOD, base^2 % MOD, ...
    # O(n) time
    def _precomputeBasePowers(self, length: int):
        basePow = [1] * (length + 1)
        for i in range(1, length + 1):
            basePow[i] = (basePow[i - 1] * self.base) % self.mod
        return basePow