class Solution:
    def maxProductPair(self, nums: list[int], target: int) -> list[int]:
        mxP = -inf
        res = None
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j: continue
                if nums[i] + nums[j] == target and nums[i] > nums[j]:
                    p = nums[i] * nums[j]
                    if p > mxP:
                        mxP = p
                        res = [i, j]
        return res if res is not None else [-1, -1]
                    