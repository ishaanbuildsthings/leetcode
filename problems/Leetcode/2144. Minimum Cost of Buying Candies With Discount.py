class Solution:
    def minimumCost(self, cost: List[int]) -> int:
        # can do bucket sort
        cost.sort()
        res = 0
        for i in range(len(cost) - 1, -1, -1):
            dist = len(cost) - i
            if dist % 3 == 0:
                continue
            res += cost[i]
        return res