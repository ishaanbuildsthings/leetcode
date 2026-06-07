class Solution:
    def sumOfGoodIntegers(self, n: int, k: int) -> int:
        res = 0
        for num in range(1, 1000):
            if abs(n - num) <= k:
                if num & n == 0:
                    res += num
        return res