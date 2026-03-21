class Solution:
    def countPartitions(self, nums: List[int]) -> int:
        res = 0
        left = nums[0]
        right = sum(nums) - left
        if abs(left - right) % 2 == 0:
            res += 1
        for i in range(1, len(nums) - 1):
            left += nums[i - 1]
            right -= nums[i - 1]
            if abs(left - right) % 2 == 0:
                res += 1
        
        return res