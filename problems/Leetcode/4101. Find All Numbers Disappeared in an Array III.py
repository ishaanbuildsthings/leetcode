class Solution:
    def findDisappearedNumbers(self, nums: list[int], lower: int, upper: int) -> list[list[int]]:
        nums = sorted([x for x in nums if lower <= x <= upper])
        res = []
        for i, v in enumerate(nums):
            prev = nums[i-1] + 1 if i else lower
            right = v - 1
            if right >= prev:
                res.append([prev, right])
        if nums and nums[-1] + 1 <= upper:
            res.append([nums[-1] + 1, upper])
        if not nums:
            res.append([lower, upper])
        return res