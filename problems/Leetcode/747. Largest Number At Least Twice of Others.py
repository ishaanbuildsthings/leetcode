class Solution:
    def dominantIndex(self, nums: List[int]) -> int:
        res = None
        big = -inf
        big2 = -inf
        for i, num in enumerate(nums):
            if num >= big:
                big2 = big
                big = num
                res = i
            elif num >= big2:
                big2 = num
        
        return res if big >= 2 * big2 else -1