class Solution:
    def getLucky(self, s: str, k: int) -> int:
        def solveForNum(num):
            res = 0
            while num:
                res += (num % 10)
                num //= 10
            return res
        
        res = int(''.join(str(ord(char) - ord('a') + 1) for char in s))
        for _ in range(k):
            res = solveForNum(res)
        
        return res