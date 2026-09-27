class Solution:
    def maxEarnings(self, meetings: list[list[int]]) -> int:
        meetings.sort()
        n = len(meetings)

        early = [n] * n # if we take meeting i, what is the earliest next one we can take
        for i in range(len(meetings)):
            l, r, rev = meetings[i]

            # binary search for earliest meeting starting >= our end
            L = i + 1
            R = n - 1
            resI = None
            while L <= R:
                m = (L + R) // 2
                ml, mr, mrev = meetings[m]
                if ml >= r:
                    resI = m
                    R = m - 1
                else:
                    L = m + 1
            if resI is not None:
                early[i] = resI
                

        @cache
        def dp(i, hasTaken, recentSkip):
            if i == n:
                if recentSkip:
                    return -inf
                return 0

            res = -inf

            l, r, rev = meetings[i]

            if i != n - 1:
                # if we skip this
                ntaken = hasTaken
               

                nextL, nextR, nextRev = meetings[i + 1]

                gain = (nextL - l) if hasTaken else 0

                nextDp = dp(i + 1, ntaken, True) + gain
                res = max(res, nextDp)

            # take this
            ntaken = True
            nextI = early[i]

            takeAndEnd = rev
            res = max(res, takeAndEnd)

            nextL = 0
            nextR = 0
            nextRev = 0
            gain = 0
            if nextI != n:
                nextL, nextR, nextRev = meetings[nextI]
                gain = nextL - r
            

            # take and continue, but we must take more
            nextDp = dp(nextI, ntaken, False) + rev + gain

            res = max(res, nextDp)
            return res

        answer = dp(0, False, True)
        dp.cache_clear()

        return answer
            
            
            