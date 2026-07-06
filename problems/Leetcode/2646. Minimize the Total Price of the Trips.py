class Solution:
    def minimumTotalPrice(self, n: int, edges: List[List[int]], price: List[int], trips: List[List[int]]) -> int:
        children = defaultdict(list)
        adjMap = defaultdict(list)
        for a, b in edges:
            adjMap[a].append(b)
            adjMap[b].append(a)

        parents = [None] * n
        
        def dfs(node, parent):
            parents[node] = parent
            for adj in adjMap[node]:
                if adj == parent:
                    continue
                children[node].append(adj)
                dfs(adj, node)
        
        dfs(0, -1)

        # find the LCA for two nodes

        @cache
        def ancestor(node, power):
            if power == 0:
                return parents[node]
            halfwayAncestor = ancestor(node, power - 1)
            fullAncestor = ancestor(halfwayAncestor, power - 1)
            return fullAncestor
        
        depths = [None] * n
        def markDepths(node, currDepth):
            depths[node] = currDepth
            for child in children[node]:
                markDepths(child, currDepth + 1)
        markDepths(0, 0)

        @cache
        def kthAncestor(node, k):
            if not k:
                return node
            # find the biggest power of 2 <= k
            powBit = k.bit_length() - 1
            return kthAncestor(ancestor(node, powBit), k - (1 << powBit))


        def lca(node1, node2):
            depthDiff = abs(depths[node1] - depths[node2])

            # bring the nodes to the same level
            if depths[node1] > depths[node2]:
                node1 = kthAncestor(node1, depthDiff)
            elif depths[node2] > depths[node1]:
                node2 = kthAncestor(node2, depthDiff)
            
            # if when at the same level, they are the same node, that is the lca
            if node1 == node2:
                return node1
            
            for power in range(10, -1, -1):
                node1Jump = ancestor(node1, power)
                node2Jump = ancestor(node2, power)
                # if these are the same, we shouldnt jump so high
                if node1Jump == node2Jump:
                    continue
                node1 = node1Jump
                node2 = node2Jump
            
            return parents[node1]
        
        visits = Counter()

        def collect(node, ancestor):
            visits[node] += 1
            if node == ancestor:
                return
            collect(parents[node], ancestor)
        
        for a, b in trips:
            LCA = lca(a, b)
            collect(a, LCA)
            collect(b, LCA)
            visits[LCA] -= 1 # dedupe
        
        overallValues = [None] * n
        for node in range(n):
            timesVisited = visits[node]
            priceNode = price[node]
            totalPrice = timesVisited * priceNode
            overallValues[node] = totalPrice
        
        @cache
        def dp(node, isAboveHalved):
            # base case, leaf node
            if not children[node]:
                if not isAboveHalved:
                    return overallValues[node] // 2
                return overallValues[node]

            res = inf
            # if the above is halved, we must not halve ourselves, and have free reign over children
            ifChildrenCanBeHalved = sum(dp(child, False) for child in children[node])

            if isAboveHalved:
                return overallValues[node] + ifChildrenCanBeHalved
            
            # if the above is not halved, we can either not halve ourselves, or we can
            dontHalveOurself = overallValues[node] + ifChildrenCanBeHalved
            ifChildrenCannotBeHalved = sum(dp(child, True) for child in children[node])
            halveOurself = (overallValues[node] // 2) + ifChildrenCannotBeHalved
            return min(dontHalveOurself, halveOurself)
        
        return dp(0, False)

            

        
        

        





        