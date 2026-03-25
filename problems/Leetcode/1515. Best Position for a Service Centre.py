class Solution:
    def getMinDistSum(self, positions: List[List[int]]) -> float:
        EPSILON = 10**(-6)

        def cost(x, y):
            totCost = 0
            for px, py in positions:
                totCost += math.sqrt(abs(px - x)**2 + abs(py - y)**2)
            return totCost
        
        # freeze the x coordinate, what is the best Y?
        def bestY(x):
            l = 0
            r = 100
            while (l + EPSILON) <= r:
                third = (r - l) / 3
                m1 = l + third
                m2 = m1 + third
                c1 = cost(x, m1)
                c2 = cost(x, m2)
                if c1 <= c2:
                    r = m2
                else:
                    l = m1
            return l
        
        # find the best X
        l = 0
        r = 100
        res = inf
        while (l + EPSILON) <= r:
            third = (r - l) / 3
            m1 = l + third
            m2 = m1 + third
            c1 = cost(m1, bestY(m1))
            c2 = cost(m2, bestY(m2))
            res = min(res, c1, c2)
            if c1 <= c2:
                r = m2
            else:
                l = m1
        
        return res
