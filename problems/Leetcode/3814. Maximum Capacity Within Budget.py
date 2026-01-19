class Solution:
    def maxCapacity(self, costs: List[int], capacity: List[int], budget: int) -> int:
        budget -= 1
        z = list(zip(costs, capacity))
        z.sort()
        pfMaxCap = [-1] * len(costs)
        curr = -1
        for i in range(len(costs)):
            curr = max(curr, z[i][1])
            pfMaxCap[i] = curr

        res = 0
        for i, (cost, cap) in enumerate(z):
            if cost > budget:
                break
            remain = budget - cost
            # bin search for rightmost cost we can take
            l = 0
            r = i - 1
            resI = None
            while l <= r:
                m = (r + l) // 2
                if z[m][0] <= remain:
                    resI = m
                    l = m + 1
                else:
                    r = m - 1
            if resI is None:
                res = max(res, cap)
                continue
            res = max(res, cap + pfMaxCap[resI])

        return res
            