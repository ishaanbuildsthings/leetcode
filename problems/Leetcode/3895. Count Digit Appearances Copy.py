class Solution:
    def countDigitOccurrences(self, nums: list[int], digit: int) -> int:
        res = 0
        for v in nums:
            for x in str(v):
                if int(x) == digit:
                    res += 1
        return res