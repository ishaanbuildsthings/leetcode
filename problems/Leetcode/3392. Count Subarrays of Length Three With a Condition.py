class Solution:
    def countSubarrays(self, nums: List[int]) -> int:
        res = 0
        for start in range(len(nums) - 2):
            if nums[start] + nums[start + 2] == 0.5 * nums[start + 1]:
                res += 1
        return res