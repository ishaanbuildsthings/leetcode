class Solution:
    def maxScore(self, nums: List[int]) -> int:
        res = -inf
        for i in range(len(nums)):
            dupe = nums[:]
            dupe.pop(i)
            resHere = lcm(*dupe) * gcd(*dupe)
            res = max(res, resHere)
        res = max(res, lcm(*nums) * gcd(*nums))
        return res