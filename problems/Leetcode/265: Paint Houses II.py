class Solution:
    def minCostII(self, costs: List[List[int]]) -> int:
        n = len(costs)
        k = len(costs[0])
        min1 = 0
        min2 = 0
        color1 = -1
        for i in range(n):
            nmin1 = inf
            nmin2 = inf
            ncolor1 = None
            for color in range(k):
                cost = costs[i][color]
                if color != color1:
                    ncost = cost + min1
                    if ncost < nmin1:
                        nmin2 = nmin1
                        nmin1 = ncost
                        ncolor1 = color
                    elif ncost < nmin2:
                        nmin2 = ncost
                else:
                    ncost = cost + min2
                    if ncost < nmin1:
                        nmin2 = nmin1
                        nmin1 = ncost
                        ncolor1 = color
                    elif ncost < nmin2:
                        nmin2 = ncost

            min1 = nmin1
            min2 = nmin2
            color1 = ncolor1
        
        return min1

