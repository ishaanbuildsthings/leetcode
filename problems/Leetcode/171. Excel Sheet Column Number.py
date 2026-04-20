class Solution:
    def titleToNumber(self, columnTitle: str) -> int:
        res = 0
        for i in range(len(columnTitle) - 1, -1, -1):
            multiplier = 26**(len(columnTitle) - i - 1)
            res += (ord(columnTitle[i]) - ord('A') + 1) * multiplier
        return res