class Solution:
    def maximumTeamSize(self, startTime: list[int], endTime: list[int]) -> int:
        n = len(startTime)
        res = 0
        sortedStart = sorted(startTime)
        sortedEnd = sorted(endTime)
        for i in range(n):
            l, r = startTime[i], endTime[i]
            # number ending strictly less than l
            lefts = bisect_left(sortedEnd, l)
            # number strictly starting <= r
            rights = bisect_right(sortedStart, r)
            # number strictly starting > r
            rights = n - rights
            intersect = n - (lefts + rights)
            res = max(res, intersect)
        return res
