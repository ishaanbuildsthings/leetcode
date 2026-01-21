class Solution:
    def longestSubsequence(self, nums: List[int]) -> int:
        xor = 0
        for v in nums:
            xor ^= v
        
        if xor != 0:
            return len(nums)

        if max(nums) > 0:
            return len(nums) - 1
        
        return 0