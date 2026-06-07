class Solution:
    def findLengthOfLCIS(self, nums: List[int]) -> int:
        curr = res = 1

        for i in range(1, len(nums)):
            if nums[i] > nums[i - 1]:
                curr += 1
                res = max(curr, res)
            else:
                curr = 1
        
        return res