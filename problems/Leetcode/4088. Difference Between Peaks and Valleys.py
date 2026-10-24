class Solution:
    def peakValleyDifference(self, nums: list[int]) -> int:
        res = 0
        for i in range(1, len(nums) - 1):
            prev = nums[i - 1]
            curr = nums[i]
            nxt = nums[i + 1]
            isPeak = prev < curr > nxt
            isValley = prev > curr < nxt
            if isPeak:
                res += curr
            if isValley:
                res -= curr
        return res