class Solution:
    def zeroFilledSubarray(self, nums: List[int]) -> int:
        streak = 0
        res = 0
        for num in nums:
            if num:
                streak = 0
            else:
                streak += 1
            res += streak
        return res