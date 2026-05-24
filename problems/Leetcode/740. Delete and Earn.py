class Solution:
    def deleteAndEarn(self, nums: List[int]) -> int:
        counts = collections.Counter(nums)
        # each number points to the number biggest than it, except for the biggest which points to inf
        bigger = {}
        parsed = list(set(sorted(nums)))
        for i in range(len(parsed) - 1):
            num = parsed[i]
            bigger[num] = parsed[i + 1]
        bigger[parsed[-1]] = float('inf')

        # cache[num] tells us the answer to the subproblem when only elements >= num are left
        @cache
        def dp(num):
            # base case
            if num == float('inf'):
                return 0
            # if we skip this number, we check the next
            ifSkip = dp(bigger[num])
            # if we take this number, we can either take the next, or the next next, if next is adjacent
            if bigger[num] == num + 1:
                ifTake = counts[num] * num + dp(bigger[bigger[num]])
            else:
                ifTake = counts[num] * num + dp(bigger[num])
            
            return max(ifSkip, ifTake)
        return dp(min(nums))