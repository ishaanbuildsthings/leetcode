# https://leetcode.com/problems/count-subarrays-with-score-less-than-k/description/
# difficulty: hard
# tags: sliding window variable

# Solution, O(n) time O(1) space

class Solution:
    def countSubarrays(self, nums: List[int], k: int) -> int:
        l = r = res = currSum = 0
        while r < len(nums):
            currSum += nums[r]
            while currSum * (r - l + 1) >= k:
                lostNum = nums[l]
                currSum -= lostNum
                l += 1
            res += (r - l + 1)
            r += 1
        return res