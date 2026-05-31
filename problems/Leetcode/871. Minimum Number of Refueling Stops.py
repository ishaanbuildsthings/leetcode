from sortedcontainers import SortedList
class Solution:
    def minRefuelStops(self, target: int, startFuel: int, stations: List[List[int]]) -> int:
        avail = SortedList()

        curr = startFuel
        stations.append([target, 0])
        stations.sort()

        spends = 0

        if stations:
            curr -= stations[0][0]

        for i in range(len(stations)):
            pos, fuel = stations[i]
            while curr < 0:
                if not avail:
                    return -1
                prevMax = avail[-1]
                curr += prevMax
                avail.pop(-1)
                spends += 1
            avail.add(fuel)
            if pos >= target:
                break
            if i < len(stations) - 1:
                nxtPos = stations[i + 1][0]
                curr -= (nxtPos - pos)
        
        return spends
