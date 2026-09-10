class Solution:
    def minimumRelativeLosses(self, prices: List[int], queries: List[List[int]]) -> List[int]:
        prices.sort()
        pf = []
        curr = 0
        for v in prices:
            curr += v
            pf.append(curr)
        
        def query(l, r):
            return pf[r] - (pf[l-1] if l else 0)
        
        def answerQ(k, mQuery):
            # find latest index with cost <= k
            l = 0
            r = len(prices) - 1
            resI = -1
            while l <= r:
                m = (l + r) // 2
                if prices[m] <= k:
                    resI = m
                    l = m + 1
                else:
                    r = m - 1
            
            countLteK = resI + 1
            
            def bobCostPrefix(taken):
                paidFully = min(countLteK, taken)
                paidFullyTotal = query(0, paidFully - 1) if paidFully else 0
                paidPartially = taken - paidFully
                paidPartiallyTotal = paidPartially * k
                return paidFullyTotal + paidPartiallyTotal
            
            def bobCostSuffix(taken):
                if taken == 0:
                    return 0
                start = len(prices) - taken
                paidFully = max(0, min(taken, countLteK - start))
                paidFullyTotal = query(start, start + paidFully - 1) if paidFully else 0
                paidPartially = taken - paidFully
                paidPartiallyTotal = paidPartially * k
                return paidFullyTotal + paidPartiallyTotal
            
            def aliceCostSuffix(taken):
                if taken == 0:
                    return 0
                start = len(prices) - taken
                total = query(start, len(prices) - 1)
                return total - bobCostSuffix(taken)
            
            def aliceCostPrefix(taken):
                total = query(0, taken - 1) if taken else 0
                return total - bobCostPrefix(taken)
            
            def relativeCost(takenPf, takenSuff):
                bob = bobCostPrefix(takenPf) + bobCostSuffix(takenSuff)
                alice = aliceCostPrefix(takenPf) + aliceCostSuffix(takenSuff)
                return bob - alice

            # ternary search for how much of the prefix we use
            l = 0
            r = mQuery - 1 # prevent oob on m2
            res = mQuery
            while l <= r:
                m1 = (l + r) // 2
                m2 = m1 + 1
                c1 = relativeCost(m1, mQuery - m1)
                c2 = relativeCost(m2, mQuery - m2)
                if c1 <= c2:
                    res = m1
                    r = m1 - 1
                else:
                    l = m1 + 1
            
            return relativeCost(res, mQuery - res)

        
        return [answerQ(*q) for q in queries]