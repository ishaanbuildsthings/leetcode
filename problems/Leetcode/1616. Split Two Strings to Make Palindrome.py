# Solution 1 greedy
class Solution:
    def checkPalindromeFormation(self, a: str, b: str) -> bool:
        # take some prefix of one + some suffix of two
        def check(one, two):
            l = 0
            r = len(one) - 1
            while l < r:
                if one[l] == two[r]:
                    l += 1
                    r -= 1
                    continue
                else:
                    break
            if l >= r:
                return True
            # take a big prefix of one
            mid = one[l:r+1]
            if mid == mid[::-1]:
                return True
            mid = two[l:r+1]
            # take a small prefix of one
            if mid == mid[::-1]:
                return True
            return False
        return check(a,b) or check(b,a)
        

        
# Solution 2, cursed AF hashing
# # Works on strings and arrays
# class PalindromeHashing:
#     # List of good prime numbers for hashing, will choose randomly if not provided
#     GOOD_MODS = [1000000007, 1000000009, 998244353, 999999937, 999999929,
#                  999999893, 999999797, 999999761, 999999757, 999999751,
#                  999999739, 999999733, 999999721, 999999697, 999999691,
#                  999999679, 999999673, 999999661, 999999649, 999999637,
#                  999999631, 999999587, 999999599, 999999577, 999999563,
#                  999999527, 999999519, 999999503, 999999491, 999999487]

#     # O(n) time
#     # Base is ideally prime, and bigger than the max value hashFunc can output, otherwise we can get collisions e.g. base=3, [1,1] collides with [4]. Base should also be coprime to mod I think?
#     def __init__(self, stringOrArr: str, base: int = 26, mod: int = None, hashFunc=lambda x: ord(x) - ord('a') + 1):
#         self.window = list(stringOrArr)
#         self.base = base
#         self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
#         self.hashFunc = hashFunc # The output coefficient for a single value, like ord('a')
#         self.prefixHashes = self._buildPrefixHashes(stringOrArr) # O(n) time
#         self.reversePrefixHashes = self._buildReversePrefixHashes(stringOrArr) # O(n) time
#         self.basePow = self._precomputeBasePowers(len(stringOrArr)) # O(n) time

#     # Builds the prefix hashes of the string/array, prefixHashes[i] is for string[:i], so prefixHashes[0] is for the empty string/array
#     # O(n) time
#     def _buildPrefixHashes(self, stringOrArr: str):
#         prefixHashes = [0] * (len(stringOrArr) + 1)
#         for i in range(1, len(stringOrArr) + 1):
#             prefixHashes[i] = (prefixHashes[i - 1] * self.base + self.hashFunc(stringOrArr[i - 1])) % self.mod
#         return prefixHashes

#     # Builds the prefix hashes of the reversed string/array, so reversedPrefixHashes[2] is the hash of the first two character prefix, but that prefix is reversed. reversedPrefixHashes[0] is for the empty string
#     # string = 'abc', reverse prefixes are 'a', 'ba', 'cba'
#     # O(n) time
#     def _buildReversePrefixHashes(self, stringOrArr: str):
#         reversePrefixHashes = [0] * (len(stringOrArr) + 1)
#         for i in range(1, len(stringOrArr) + 1):
#             reversePrefixHashes[i] = (reversePrefixHashes[i - 1] * self.base + self.hashFunc(stringOrArr[-i])) % self.mod
#         return reversePrefixHashes

#     # Precompute powers of base, so base^0 % MOD, base^1 % MOD, base^2 % MOD, ...
#     # O(n) time
#     def _precomputeBasePowers(self, length: int):
#         basePow = [1] * (length + 1)
#         for i in range(1, length + 1):
#             basePow[i] = (basePow[i - 1] * self.base) % self.mod
#         return basePow

#     # Gets the hash of a substring/subarray [left...right] using math
#     # O(1) time
#     def getHashForSubstring(self, left: int, right: int) -> int:
#         return (self.prefixHashes[right + 1] - self.prefixHashes[left] * self.basePow[right - left + 1]) % self.mod

#     # Gets the hash of a reversed section of the string/array, uses the original string/array indices
#     # O(1) time
#     def getHashForReversedSubstring(self, originalStringLeft: int, originalStringRight: int) -> int:
#         left = len(self.window) - originalStringRight - 1
#         right = len(self.window) - originalStringLeft
#         return (self.reversePrefixHashes[right] - self.reversePrefixHashes[left] * self.basePow[right - left]) % self.mod

#     # O(1) time
#     def isPalindrome(self, left: int, right: int) -> bool:
#         return self.getHashForSubstring(left, right) == self.getHashForReversedSubstring(left, right)

#     # Gets the hash of a string/array
#     # O(n) time
#     def hash(self, stringOrArr: str) -> int:
#         res = 0
#         for c in stringOrArr:
#             coefficient = self.hashFunc(c)
#             res = (res * self.base + coefficient) % self.mod
#         return res

#     # Adds a character to the end of the string/array and updates hashes
#     # O(1) time
#     def addChar(self, c: str):
#         self.window.append(c)
#         if len(self.window) > len(self.basePow):
#             self.basePow.append((self.basePow[-1] * self.base) % self.mod)
#         self.prefixHashes.append((self.prefixHashes[-1] * self.base + self.hashFunc(c)) % self.mod)
#         self.reversePrefixHashes.append((self.reversePrefixHashes[-1] * self.base + self.hashFunc(c)) % self.mod)

#     # Removes the last character from the string/array and updates hashes
#     # O(1) time
#     def popChar(self):
#         if len(self.window) == 0:
#             return
#         self.window.pop()
#         self.prefixHashes.pop()
#         self.reversePrefixHashes.pop()

#     # Gets the hash of the entire window
#     # O(1) time
#     def getHash(self) -> int:
#         return self.prefixHashes[-1]

#     # Returns the current window as a list
#     # O(1) time
#     def getCurrentWindow(self) -> str:
#         return self.window

#     # Returns the length of the current window
#     # O(1) time
#     def length(self) -> int:
#         return len(self.window)

# class Solution:
#     def checkPalindromeFormation(self, a: str, b: str) -> bool:
#         n   = len(a)
#         MOD = 999999637

#         hA = PalindromeHashing(a, mod=MOD)
#         hB = PalindromeHashing(b, mod=MOD)

#         base_pow = hA.basePow

#         def cat(hash_left, len_right, hash_right):
#             return (hash_left * base_pow[len_right] + hash_right) % MOD

#         def ok(pref, suff):
#             for i in range(n + 1):
#                 len_pref = i
#                 len_suff = n - i

#                 h_pref = 0 if i == 0 else pref.getHashForSubstring(0, i - 1)
#                 h_suff = 0 if i == n else suff.getHashForSubstring(i, n - 1)
#                 forward = cat(h_pref, len_suff, h_suff)

#                 h_rev_pref = 0 if i == 0 else pref.getHashForReversedSubstring(0, i - 1)
#                 h_rev_suff = 0 if i == n else suff.getHashForReversedSubstring(i, n - 1)
                
#                 reverse = cat(h_rev_suff, len_pref, h_rev_pref)

#                 if forward == reverse:
#                     return True
#             return False

#         return ok(hA, hB) or ok(hB, hA)
