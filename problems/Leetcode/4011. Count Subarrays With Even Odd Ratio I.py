class Solution:
    def countRatioSubarrays(self, nums: list[int], a: int, b: int) -> int:
        res = 0
        n = len(nums)
        for l in range(n):
            evens = 0
            odds = 0
            for r in range(l, n):
                v = nums[r]
                if v % 2:
                    odds += 1
                else:
                    evens += 1
                if not odds:
                    continue
                    
                if (evens / odds) <= (a / b):
                    res += 1
        return res