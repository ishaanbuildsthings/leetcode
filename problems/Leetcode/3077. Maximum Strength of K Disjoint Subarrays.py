class Solution:
    def maximumStrength(self, nums: List[int], k: int) -> int:
        n = len(nums)

        # 1 means we are active
        # the state is the previous cell
        @cache
        def dp(i, completed, state):
            if completed > k:
                return -inf
            if i == n:
                return 0 if completed == k else -inf

            prefix = k - completed
            sign = 1 if (k - prefix) % 2 == 0 else -1
            
            # not in an active
            if state == 0:
                ifSkip = dp(i + 1, completed, 0)
                ifStart = prefix * sign * nums[i] + dp(i + 1, completed, 1)
                ifStartAndEnd = prefix * sign * nums[i] + dp(i + 1, completed + 1, 0)
                return max(ifSkip, ifStart, ifStartAndEnd)
            
            ifCont = prefix * sign * nums[i] + dp(i + 1, completed, 1)
            ifEnd = dp(i + 1, completed + 1, 0)
            ifStartAndEnd = prefix * sign * nums[i] + dp(i + 1, completed + 1, 0)
            return max(ifCont, ifEnd, ifStartAndEnd)
        
        ans = dp(0, 0, 0)
        dp.cache_clear()
        return ans

