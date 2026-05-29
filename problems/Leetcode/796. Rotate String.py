# Works only on lowercase letters strings, because the logic for getting the coefficient of a hash value is baked into the class.
class IncrementalHashing:
    # List of good prime numbers for hashing, will choose randomly if not provided
    GOOD_MODS = [1000000007, 1000000009, 998244353, 999999937, 999999929,
                 999999893, 999999797, 999999761, 999999757, 999999751,
                 999999739, 999999733, 999999721, 999999697, 999999691,
                 999999679, 999999673, 999999661, 999999649, 999999637,
                 999999631, 999999587, 999999599, 999999577, 999999563,
                 999999527, 999999519, 999999503, 999999491, 999999487]

    # Base is ideally prime, and bigger than ord(some character) since we don't necessarily use 'a'->1, the base values can be big, so base needs to be big enough to not have collisions
    # O(n) time
    def __init__(self, string: str, base: int = 911, mod: int = None):
        self.window = deque(string)  # We maintain the characters
        self.base = base
        self.mod = mod if mod is not None else random.choice(self.GOOD_MODS)
        self.baseInv = pow(self.base, -1, self.mod)
        self.basePow = [1]  # base^0 % mod
        self.hashValue = 0
        # Build base pows + the initial hash
        # O(n) time
        for i, c in enumerate(self.window):
            if i >= len(self.basePow):
                self.basePow.append((self.basePow[-1] * self.base) % self.mod)
            coefficient = ord(c)
            self.hashValue = (self.hashValue * self.base + coefficient) % self.mod

    # O(1) time
    def getHash(self) -> int:
        return self.hashValue

    # Adds a character to the end of the string and updates the hash
    # O(1) time
    def addChar(self, c: str):
        self.window.append(c)
        coefficient = ord(c)
        self.hashValue = (self.hashValue * self.base + coefficient) % self.mod
        if len(self.window) >= len(self.basePow):
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)

    # Removes the last character from the string and updates the hash
    # O(1) time
    def popChar(self):
        if len(self.window) == 0:
            return
        c = self.window.pop()
        coefficient = ord(c)
        self.hashValue = (self.hashValue - coefficient) * self.baseInv % self.mod

    # Adds a character to the beginning of the string and updates the hash
    # O(1) time
    def addCharLeft(self, c: str):
        self.window.appendleft(c)
        coefficient = ord(c)
        self.hashValue = (coefficient * self.basePow[len(self.window) - 1] + self.hashValue) % self.mod
        if len(self.window) >= len(self.basePow):
            self.basePow.append((self.basePow[-1] * self.base) % self.mod)

    # Removes the first character from the string and updates the hash
    # O(1) time
    def popCharLeft(self):
        if len(self.window) == 0:
            return
        c = self.window.popleft()
        coefficient = ord(c)
        self.hashValue = (self.hashValue - coefficient * self.basePow[len(self.window)]) % self.mod

    # Slides the window to the right by popping from the left and adding a character to the right
    # O(1) time
    def slideRight(self, c: str):
        self.popCharLeft()
        self.addChar(c)

    # Slides the window to the left by popping from the right and adding a character to the left
    # O(1) time
    def slideLeft(self, c: str):
        self.popChar()
        self.addCharLeft(c)

    def getCurrentWindow(self) -> str:
        return self.window

    # Gets the hash of a string
    # O(n) time
    def hash(self, s: str) -> int:
        res = 0
        for c in s:
            coefficient = ord(c)
            res = (res * self.base + coefficient) % self.mod
        return res
class Solution:
    def rotateString(self, s: str, goal: str) -> bool:
        goalHash = IncrementalHashing(goal,mod=10**9+7).getHash()
        sHash = IncrementalHashing(s,mod=10**9+7)
        if sHash.getHash() == goalHash:
            return True
        for i in range(len(s)):
            sHash.popCharLeft()
            sHash.addChar(s[i])
            if sHash.getHash() == goalHash:
                return True
        return False