class Solution:
    def maximumMedianSum(self, nums: List[int]) -> int:
        # nums = [21,13,23,22,50,24]
        nums.sort()
        res = 0
        for i in range(len(nums) // 3):
            right = len(nums) - (2*i) - 1
            mid = right - 1
            res += nums[mid]
        return res