class Solution:
    def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
        curr = res = 0
        for i in range(len(nums)):
            if nums[i] == 1:
                curr += 1
                res = max(res, curr)
            else:
                curr = 0
        return res