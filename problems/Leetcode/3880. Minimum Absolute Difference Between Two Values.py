class Solution:
    def minAbsoluteDifference(self, nums: list[int]) -> int:
        res = inf
        for i in range(len(nums)):
            for j in range(len(nums)):
                if (nums[i] == 1) and (nums[j] == 2):
                    diff = abs(i-j)
                    res = min(res, diff)
        return res if res != inf else -1