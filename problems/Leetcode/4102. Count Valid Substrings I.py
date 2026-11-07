class Solution:
    def countValidSubstrings(self, s: str) -> int:
        res = 0
        n = len(s)
        l = 0
        for i, v in enumerate(s):
            if i >= 2 and s[i-2:i+1] == 'abc':
                l = i - 1
            res += i - l + 1
        return res