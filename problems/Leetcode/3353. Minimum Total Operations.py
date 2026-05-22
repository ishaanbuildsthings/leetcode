class Solution:
    def minOperations(self, nums: List[int]) -> int:
        res = 0
        for i in range(len(nums) - 1):
            if nums[i] != nums[i+1]:
                res += 1
        return res