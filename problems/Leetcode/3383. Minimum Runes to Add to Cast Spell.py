class Solution:
    def minRunesToAdd(self, n: int, crystals: List[int], flowFrom: List[int], flowTo: List[int]) -> int:
        g = [[] for _ in range(n)]
        rev = [[] for _ in range(n)]
        E = len(flowFrom)
        for i in range(E):
            g[flowFrom[i]].append(flowTo[i])
            rev[flowTo[i]].append(flowFrom[i])
        
        finishOrder = []
        seen = [False] * n
        def forwardDfs(node):
            seen[node] = True
            for adjN in g[node]:
                if seen[adjN]: continue
                forwardDfs(adjN)
            finishOrder.append(node)
        
        for node in range(n):
            if not seen[node]:
                forwardDfs(node)

        comp = [None] * n
        currComponentId = 0

        def revDfs(node):
            comp[node] = currComponentId
            for adjN in rev[node]:
                if comp[adjN] is not None:
                    continue
                revDfs(adjN)
        
        for node in finishOrder[::-1]:
            if comp[node] is not None:
                continue
            revDfs(node)
            currComponentId += 1
        
        numComponents = currComponentId
        compsWithCrystal = [False] * numComponents
        for crystal in crystals:
            compsWithCrystal[comp[crystal]] = True

        revG2 = [[] for _ in range(numComponents)]
        for i in range(E):
            node1 = flowFrom[i]
            node2 = flowTo[i]
            comp1 = comp[node1]
            comp2 = comp[node2]
            if comp1 == comp2:
                continue
            revG2[comp2].append(comp1)
        
        res = 0
        for compId in range(numComponents):
            if not compsWithCrystal[compId] and not revG2[compId]:
                res += 1
        
        return res