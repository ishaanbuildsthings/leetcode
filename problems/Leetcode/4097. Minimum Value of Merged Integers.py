class Solution:
    def minMergedInteger(self, nums: list[int]) -> int:
        res = inf
        for i in range(0, len(nums) - 1, 2):
            left = str(nums[i])
            right = str(nums[i + 1])
            # print(left, right)
            tot = int(left + right)
            res = min(res, tot)
        return res