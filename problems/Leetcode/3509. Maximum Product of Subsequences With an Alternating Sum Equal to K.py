class Solution:
    def maxProduct(self, nums: List[int], k: int, limit: int) -> int:
        # looks like 150 indices * 1800 possible sums * 5000 products * 2 * 2 =
        # 20,000 * 150 * 1800 = ~8e9
        # but 1800 and products aren't indepedent states
        # also theres actually only ~395 procuts due to the only primes being 2 3 5 7 11

        @cache
        def dp(i, currSum, currProd, hasTaken, isAdding):
            if currSum == k and currProd <= limit and hasTaken:
                resHere = currProd
            else:
                resHere = -inf
            if i == len(nums):
                return resHere
            
            newSumIfTake = (nums[i] + currSum) if isAdding else (currSum - nums[i])
            newProd = currProd * nums[i]
            if newProd > limit:
                newProd = limit + 1 # represents overflow, we need to still use this because we can zero out the value if we multiply by a 0
            newIsAdding = not isAdding

            ifTake = dp(i + 1, newSumIfTake, newProd, True, newIsAdding)
            ifSkip = dp(i + 1, currSum, currProd, hasTaken, isAdding)

            return max(resHere, ifTake, ifSkip)
        
        ans = dp(0,0,1,False,True)
        dp.cache_clear()
        if ans == -inf:
            return -1
        return ans