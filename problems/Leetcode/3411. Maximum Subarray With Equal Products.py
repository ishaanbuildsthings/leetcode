class Solution:
    def maxLength(self, nums: List[int]) -> int:
        res = 0
        for l in range(len(nums)):
            for r in range(l, len(nums)):
                g = gcd(*nums[l:r+1])
                LCM = lcm(*nums[l:r+1])
                mult = 1
                for i in range(l, r + 1):
                    num = nums[i]
                    mult *= num
                if mult == g * LCM:
                    res = max(res, r - l + 1)
        return res