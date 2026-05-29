class Solution:
    def subarraySum(self, nums: List[int]) -> int:
        res = 0
        for i in range(len(nums)):
            start = max(0, i - nums[i])
            if start > i:
                continue
            sub = nums[start:i + 1]
            res += sum(sub)
        return res