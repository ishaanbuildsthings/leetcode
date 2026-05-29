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
        if len(self.window) > len(self.basePow):
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
    
def biggestNumLteX(arr, x):
    idx = bisect.bisect_right(arr, x) - 1
    return arr[idx] if idx >= 0 else None


def smallestGte(arr, x):
    idx = bisect.bisect_left(arr, x)
    return arr[idx] if idx < len(arr) else None
    
class Solution:
    def shortestMatchingSubstring(self, s: str, p: str) -> int:
        if p and p[0] == '*':
            p = p[1:]
        if p and p[0] == '*':
            p = p[1:]
        if p and p[-1] == '*':
            p = p[:-1]
        if p and p[-1] == '*':
            p = p[:-1]
            
        arr = []
        for c in p:
            if c != '*':
                arr.append(c)
            else:
                if arr and arr[-1] == '*':
                    continue
                else:
                    arr.append(c)
        
        p = ''.join(arr)
        
        # simple match
        if not '*' in p:
            h0 = PalindromeHashing(s, 911, 10**9+7)
            h1 = PalindromeHashing(p, 911, 10**9+7)
            res = inf
            for l in range(len(s)):
                right = l + len(p) - 1
                if right >= len(s):
                    break
                rootHashX = h0.getHashForSubstring(l, right)
                if rootHashX == h1.getHash():
                    return len(p)
            return -1
        
        c = Counter(p)
        if c['*'] == 1:
            h0 = PalindromeHashing(s, 911, 10**9+7)
            left, right = p.split('*')
            h1 = PalindromeHashing(left, 911, 10**9+7)
            h2 = PalindromeHashing(right, 911, 10**9+7)
            i1 = []
            i2 = []
            for l in range(len(s)):
                rightEdge1 = l + len(left) - 1
                rightEdge2 = l + len(right) - 1
                if rightEdge1 < len(s):
                    rootHash = h0.getHashForSubstring(l, rightEdge1)
                    if rootHash == h1.getHash():
                        i1.append(l)
                if rightEdge2 < len(s):
                    rootHash = h0.getHashForSubstring(l, rightEdge2)
                    if rootHash == h2.getHash():
                        i2.append(l)
            res = inf
            
            for i in range(len(i1)):
                leftest = i1[i]
                # find the smallest in i2 >= leftest+left length
                lowerBound = leftest + len(left)
                smallestInI2 = smallestGte(i2, lowerBound)
                if smallestInI2 is None:
                    continue
                rightest = smallestInI2 + len(right) - 1
                size = rightest-leftest+1
                res = min(res, size)
            
            return res if res != inf else -1
                    
            
        
        print(p)
        
        
        h0 = PalindromeHashing(s, 911, 10**9+7)
        
        splits = p.split('*')
        h1 = PalindromeHashing(splits[0], 911, 10**9+7)
        h2 = PalindromeHashing(splits[1], 911, 10**9+7)
        h3 = PalindromeHashing(splits[2], 911, 10**9+7)
        
        i1 = []
        i2 = []
        i3 = []
        
        for l in range(len(s)):
            # first
            length1 = len(splits[0])
            rightEdge = l + length1 - 1
            if rightEdge < len(s):
                rootHash = h0.getHashForSubstring(l, rightEdge)
                if rootHash == h1.getHash():
                    i1.append(l)
            
            # second
            length2 = len(splits[1])
            rightEdge = l + length2 - 1
            if rightEdge < len(s):
                rootHash = h0.getHashForSubstring(l, rightEdge)
                if rootHash == h2.getHash():
                    i2.append(l)
            
            # third
            length3 = len(splits[2])
            rightEdge = l + length3 - 1
            if rightEdge < len(s):
                rootHash = h0.getHashForSubstring(l, rightEdge)
                if rootHash == h3.getHash():
                    i3.append(l)
        
#         print(f'i1: {i1}')
#         print(f'i2: {i2}')
#         print(f'i3: {i3}')
        
        res = inf
        
        # pick a middle index
        for i in range(len(i2)):
            midIndex = i2[i]
            # find the biggest left number that is <= midIndex - leftLength
            upperBarrierForLeftIndex = midIndex - len(splits[0])
            biggest = biggestNumLteX(i1, upperBarrierForLeftIndex)
            if biggest is None:
                continue
            
            # find the smallest number that is >= midIndex + midlength
            lowerBound = midIndex + len(splits[1])
            smallest = smallestGte(i3, lowerBound)
            if smallest is None:
                continue
            
            leftest = biggest
            rightest = smallest + len(splits[2]) - 1
            size = rightest-leftest+1
            res = min(res, size)
        
        return res if res != inf else -1
            
            
                
                
            
        
        
        