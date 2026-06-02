class Solution:
    def maxTaxiEarnings(self, n: int, rides: List[List[int]]) -> int:

        # there is a faster solution
        
        rides.sort()
        starts = [ride[0] for ride in rides]
        starts.append(inf) # trick to make firstIndexGT work cleanly

        # len(arr) if no number is >= threshold
        def firstIndexGTE(arr, threshold):
            index = bisect.bisect_left(arr, threshold)
            return index if index < len(arr) else len(arr)

        @cache
        def dp(i):
            if i == len(rides):
                return 0
            ifSkip = dp(i + 1)

            start, end, tip = rides[i]
            ifTakeGain = end - start + tip
            firstIndexGreaterThanEqualTripEnd = firstIndexGTE(starts, end)
            ifTake = ifTakeGain + dp(firstIndexGreaterThanEqualTripEnd)

            return max(ifSkip, ifTake)
        
        return dp(0)

            
            
            