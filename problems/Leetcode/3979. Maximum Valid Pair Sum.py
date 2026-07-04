class Solution:
    def maxValidPairSum(self, nums: list[int], k: int) -> int:
        suffMax = [-inf] * len(nums)
        curr = -inf
        for i in range(len(nums) - 1, -1, -1):
            curr = max(curr, nums[i])
            suffMax[i] = curr

        res = -inf
        for i in range(len(nums)):
            j = i + k
            if j >= len(nums): break
            res = max(res, nums[i] + suffMax[j])

        return res