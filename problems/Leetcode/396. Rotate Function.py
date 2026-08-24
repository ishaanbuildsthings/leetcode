class Solution:
    def maxRotateFunction(self, nums: List[int]) -> int:
        curr = 0
        for i in range(len(nums)):
            curr += i * nums[i]
        nextGain = sum(nums[:-1]) # can make O(1) space
        end = len(nums) - 1
        res = curr

        for i in range(len(nums)):
            lost = (len(nums) - 1) * nums[end]
            curr += nextGain
            nextGain -= nums[end - 1]
            nextGain += nums[end]
            curr -= lost
            res = max(res, curr)
            end -= 1
        
        return res