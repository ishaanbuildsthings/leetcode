from sortedcontainers import SortedList
class Solution:
    def minCost(self, nums: List[int]) -> int:
        if len(nums) <= 2:
            return max(nums)
        
        @cache
        def dp(i, prevKept):
            # print('__________')
            # print(f'dp called on i={i} prev kept: {prevKept}')
            if i >= len(nums):
                if prevKept is not None:
                    return prevKept
                return 0
            if i == len(nums) - 1:
                pool = []
                if prevKept is not None:
                    pool.append(prevKept)
                pool.append(nums[i])
                return max(pool)
            
            pool = []
            pool.append(nums[i])
            pool.append(nums[i+1])
            if prevKept is not None:
                pool.append(prevKept)
            else:
                pool.append(nums[i+2])
            pool.sort()
            # print(f'pool: {pool}')
            ifRemoveMid = pool[1] + dp(i + (3 if prevKept is None else 2), pool[-1])
            ifRemoveBig = pool[-1] + dp(i + (3 if prevKept is None else 2), pool[0])
            
            return min(ifRemoveBig, ifRemoveMid)
        
        a = dp(0, None)
        dp.cache_clear()
        return a