class Solution:
    def firstDayBeenInAllRooms(self, nextVisit: List[int]) -> int:
        M = 10**9 + 7
        n = len(nextVisit)
        @cache
        def dp(i, odd):
            if i == 0:
                return 0 if odd else 1

            # to get here an odd amount of times we go to the previous room an even amount of times
            if odd:
                return (1 + dp(i - 1, 0)) % M
            # to get here an even amount of times we have to reach this room an odd amount of times
            getHereOnce = dp(i, 1)
            # then we spend one to go to nextVisit[i]
            prevBounce = nextVisit[i]
            toGoPrevBounce = 1
            # now we have to go from prevBounce -> i
            # which is going from 0->i minus 0->prevBounce
            prevToI = (dp(i, 1) - dp(prevBounce, 1)) % M

            return (getHereOnce + toGoPrevBounce + prevToI) % M

        return dp(n - 1, 1)