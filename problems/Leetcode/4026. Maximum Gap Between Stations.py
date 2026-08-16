class Solution:
    def maximumGap(self, skill: str, station: str) -> int:

        # for every prefix of skills, tightly place
        # for every suffix, tightly place
        # now just look at the diffs


        pf = [None] * len(skill) # pf[skillI] is the index we must go up to in station
        stationI = 0
        skillI = 0
        while skillI < len(skill):
            v = skill[skillI]
            while station[stationI] != v:
                stationI += 1
            pf[skillI] = stationI
            skillI += 1
            stationI += 1

        suff = [None] * len(skill)
        stationI = len(station) - 1
        skillI = len(skill) - 1
        while skillI >= 0:
            v = skill[skillI]
            while station[stationI] != v:
                stationI -= 1
            suff[skillI] = stationI
            skillI -= 1
            stationI -= 1

        res = 0

        for i in range(len(pf) - 1):
            PF = pf[i]
            SUFF = suff[i + 1]
            dist = SUFF - PF
            res = max(res, dist)

        return res