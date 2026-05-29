class Solution:
    def countDistinct(self, s: str) -> int:
        def charToNum(char):
            return ord(char) - ord('a') + 1

        MOD = 10**12 + 7 # random mod to avoid adversarial attack

        res = 0

        seenHashes = set()
        for i in range(len(s)):
            currHash = 0
            for j in range(i, len(s)):
                currHash *= 26
                currHash += charToNum(s[j])
                currHash %= MOD
                if not currHash in seenHashes:
                    seenHashes.add(currHash)
                    res += 1
        return res
