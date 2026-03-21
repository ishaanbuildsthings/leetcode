class Solution:
    def numJewelsInStones(self, jewels: str, stones: str) -> int:
        bitset = 0
        for j in jewels:
            bitset |= 1 << ord(j) - ord('A')
        return sum(
            bitset >> ord(s) - ord('A') & 1 for s in stones
        )