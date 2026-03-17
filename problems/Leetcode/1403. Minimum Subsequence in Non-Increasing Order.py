class Solution:
    def minSubsequence(self, nums: List[int]) -> List[int]:
        # can use bucket sort
        nums.sort(reverse=True)
        tot = sum(nums)
        curr = 0
        a = []
        for i in range(len(nums)):
            curr += nums[i]
            tot -= nums[i]
            a.append(nums[i])
            if curr > tot:
                return a