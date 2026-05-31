from sortedcontainers import SortedList
class Solution:
    def maxPerformance(self, n: int, speed: List[int], efficiency: List[int], k: int) -> int:
        z = [ (efficiency[i], speed[i]) for i in range(len(speed))]
        z.sort()

        # holds (speed, efficiency)
        bottom = SortedList([(tup[1], tup[0]) for tup in z])
        top = SortedList() # holds the top k speeda


        while len(top) < (k - 1) and bottom:
            top.add(bottom.pop(0))

        totSpeeds = sum(top[i][0] for i in range(len(top)))
        res = 0

        for i in range(len(z)):
            minEff, speedHere = z[i]
            try:
                bottom.remove((speedHere, minEff))
            except:
                top.remove((speedHere, minEff))
                totSpeeds -= speedHere
            while len(top) < (k - 1) and bottom:
                addedTup = bottom.pop(0)
                top.add(addedTup)
                totSpeeds += addedTup[0]
            while bottom and top and bottom[-1] > top[0]:
                lost = top.pop(0)
                totSpeeds -= lost[0]
                bottom.add(lost)
                gained = bottom.pop(-1)
                totSpeeds += gained[0]
                top.add(gained)

            totalSpeeds = speedHere + totSpeeds
            res = max(res, totalSpeeds * minEff)
        
        return res % (10**9 + 7)



