class Solution:
    def minZeroArray(self, nums: List[int], queries: List[List[int]]) -> int:

        # solution 1, run a knapsack dp for all 10 indices checking the earliest index doable, so 10 * maxval * queries time
        # I think we could also modify our dp to return a boolean, like can we zero-out this value with the first qi queries, which suggests we can turn it into a bitset dp since we return booleans
        
        # finds the earliest query index we can finish at, or inf if we cannot
        # def solveForI(i):
        #     @cache
        #     def dp(qi, val):
        #         if val == 0:
        #             return qi - 1
        #         if val < 0:
        #             return inf
        #         if qi == len(queries):
        #             return inf
        #         ifSkip = dp(qi + 1, val)
        #         l, r, v = queries[qi]
        #         if i >= l and i <= r:
        #             ifTake = dp(qi + 1, val - v)
        #             return min(ifSkip, ifTake)
        #         return ifSkip
            
        #     ans = dp(0,nums[i])
        #     dp.cache_clear()
        #     return ans
        
        # bigI = max(solveForI(i) for i in range(len(nums)))
        # if bigI == inf:
        #     return -1
        
        
        # return bigI + 1
                

        # solution 2, for each index we do a bitset dp
        def early(i):
            bs = 1 # 0 is a doable sum
            if nums[i] == 0:
                return -1
            target = nums[i]
            for j in range(len(queries)):
                l, r, v = queries[j]
                if i < l or i > r:
                    continue
                nbs = bs | (bs << v)
                bs = nbs         
                if (1 << nums[i]) & bs:
                    return j   
            return inf
        
        mx = max(early(i) for i in range(len(nums)))
        if mx == inf:
            return -1
        return mx + 1