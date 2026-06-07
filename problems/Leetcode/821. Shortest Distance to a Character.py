class Solution:
    def shortestToChar(self, s: str, c: str) -> List[int]:
        res = [inf] * len(s)
        left = -inf
        for i, letter in enumerate(s):
            if letter == c:
                left = i
            res[i] = (i - left)
        
        right = inf
        for i in range(len(s) - 1, -1, -1):
            if s[i] == c:
                right = i
            res[i] = min(res[i], right - i)
        
        return res