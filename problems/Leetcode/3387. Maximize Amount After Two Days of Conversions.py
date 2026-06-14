class Solution:
    def maxAmount(self, initialCurrency: str, pairs1: List[List[str]], rates1: List[float], pairs2: List[List[str]], rates2: List[float]) -> float:
        adjMap1 = defaultdict(list)
        for a, b in pairs1:
            adjMap1[a].append(b)
            adjMap1[b].append(a)
        currToRate = {}
        for i in range(len(pairs1)):
            rate = rates1[i]
            pair = pairs1[i]
            pairT = tuple(pair)
            currToRate[pairT] = rate
            invRate = 1 / rate
            invPair = pair[::-1]
            invPairT = tuple(invPair)
            currToRate[invPairT] = invRate
            
        # print(currToRate)
            
        # for day 1
        bigRate = defaultdict(int)
        bigRate[initialCurrency] = 1
            
        def dfs(currency, prevCurrency, currRate):
            bigRate[currency] = currRate
            for adj in adjMap1[currency]:
                if adj == prevCurrency:
                    continue
                if not tuple([currency, adj]) in currToRate:
                    continue
                rateHere = currToRate[tuple([currency, adj])]
                newRate = currRate * rateHere
                dfs(adj, currency, newRate)
        
        dfs(initialCurrency, None, 1)
        
        # print(bigRate)
        
        
        
        
        
        # go back
        adjMap2 = defaultdict(list)
        for a, b in pairs2:
            adjMap2[a].append(b)
            adjMap2[b].append(a)
        currToRate2 = {}
        for i in range(len(pairs2)):
            rate = rates2[i]
            pair = pairs2[i]
            pairT = tuple(pair)
            currToRate2[pairT] = rate
            invRate = 1 / rate
            invPair = pair[::-1]
            invPairT = tuple(invPair)
            currToRate2[invPairT] = invRate
        

        def dfs2(currency, prevCurrency, currRate):
            if currency == initialCurrency:
                return currRate
            resHere = 0
            for adj in adjMap2[currency]:
                if adj == prevCurrency:
                    continue
                if not tuple([currency, adj]) in currToRate2:
                    continue
                rate = currToRate2[tuple([currency, adj])]
                newRate = currRate * rate
                resHere = max(resHere, dfs2(adj, currency, newRate))
            return resHere
                
        res = 0
        for outputCurr in bigRate:
            amountOut = bigRate[outputCurr]
            backToInitRate = dfs2(outputCurr, None, 1)
            res = max(res, amountOut * backToInitRate)
        return res
            