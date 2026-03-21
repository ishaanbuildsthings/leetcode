class Solution:
    def minmaxGasDist(self, stations: List[int], k: int) -> float:
        def isValid(distance):
            used = 0
            for i in range(1, len(stations)):
                gap = stations[i] - stations[i-1]
                used += gap // distance
            return used <= k
                

        l = 0
        r = max(stations)
        res = None
        while l + (10**-6) <= r:
            m = (r+l)/2
            can = isValid(m)
            if can:
                res = m
                r = m
            else:
                l = m
        return res
