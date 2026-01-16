class Solution:
    def largestSubarray(self, nums: List[int], k: int) -> List[int]:
        res = None
        big = -inf
        for i in range(len(nums) - k, -1, -1):
            if nums[i] > big:
                big = nums[i]
                res = i
        return nums[res:res+k]