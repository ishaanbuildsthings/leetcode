class Solution:
    def maximumLength(self, nums: list[int], k: int) -> int:
        nxt = [len(nums)] * len(nums)
        # premap each number to its next on right
        remainToEarly = {}
        for i in range(len(nums) - 1, -1, -1):
            v = nums[i]
            remain = v % k
            desire = (k - remain) % k
            if desire not in remainToEarly:
                remainToEarly[remain] = i
                continue
            nxt[i] = remainToEarly[desire]
            remainToEarly[remain] = i
        
        @cache
        def dp(i):
            if i == len(nums):
                return 0
            return 1 + dp(nxt[i])
        
        return max(dp(i) for i in range(len(nums)))
