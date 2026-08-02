class Solution:
    def minOperations(self, nums: List[int]) -> int:
        res = 0
        for i, num in enumerate(nums):
            prev = 0 if i == 0 else nums[i - 1]
            diff = num - prev
            if diff <= 0:
                res += (prev + 1) - num
                nums[i] = prev + 1
        return res