class Solution:
    def minCosts(self, cost: List[int]) -> List[int]:
        res = []
        prevMin = inf
        for i in range(len(cost)):
            costSwapHere = cost[i]
            res.append(min(costSwapHere, prevMin))
            prevMin = min(prevMin, costSwapHere)
        return res