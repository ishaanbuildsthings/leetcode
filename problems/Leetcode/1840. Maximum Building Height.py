class Solution:
    def maxBuilding(self, n: int, restrictions: List[List[int]]) -> int:
        restrictions.append([1, 0]) # for first building
        restrictions.append([n, inf]) # this just makes the code work nicely
        restrictions.sort()
        # we do a left to right pass first, restricting on the right and updating the restrictions in real time
        for i in range(len(restrictions) - 1):
            ht = restrictions[i][1]
            nxtHt = restrictions[i + 1][1]
            dist = restrictions[i + 1][0] - restrictions[i][0]
            restrictedRight = min(nxtHt, ht + dist)
            restrictions[i + 1][1] = restrictedRight
        
        # now the other way
        for i in range(len(restrictions) - 1, 0, -1):
            ht = restrictions[i][1]
            prevHt = restrictions[i - 1][1]
            dist = abs(restrictions[i][0] - restrictions[i - 1][0])
            restrictedLeft = min(prevHt, ht + dist)
            restrictions[i - 1][1] = restrictedLeft
        
        res = 0
        for i in range(len(restrictions) - 1):
            x1, ht1 = restrictions[i]
            x2, ht2 = restrictions[i + 1]
            steps = x2 - x1
            forUp = abs(ht2 - ht1)

            stepsForPeak = steps - forUp
            peak = (stepsForPeak // 2) + max(ht1, ht2)
            res = max(res, peak)
        
        return res