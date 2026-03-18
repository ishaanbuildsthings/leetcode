class Solution:
    def validSubarrays(self, nums: list[int], k: int) -> int:
        # basically a subarray is valid if it contains 1 peak
        # and both ends are within K from that peak
        n = len(nums)
        peak = [False] * n
        for i in range(1, n - 1):
            if nums[i] > max(nums[i-1],nums[i+1]):
                peak[i] = True
        
        prevPeak = [-1] * n
        currPeak = -1
        for i in range(n):
            prevPeak[i] = currPeak
            if peak[i]:
                currPeak = i
        
        nextPeak = [n] * n
        currPeak = n
        for i in range(n - 1, -1, -1):
            nextPeak[i] = currPeak
            if peak[i]:
                currPeak = i
        
        res = 0

        for i in range(1, n - 1):
            if not peak[i]:
                continue
            prevRange = prevPeak[i] + 1
            nextRange = nextPeak[i] - 1
            leftOpts = min(k + 1, i - prevRange + 1)
            rightOpts = min(k + 1, nextRange - i + 1)
            res += leftOpts * rightOpts
        
        return res
            