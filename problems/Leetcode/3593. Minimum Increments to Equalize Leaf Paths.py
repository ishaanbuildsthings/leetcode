# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# takes nodes from 0 to n-1 and constructs a children map rooted at 0
from collections import defaultdict
def edgeListToTree(edgeList):
    edgeMap = defaultdict(list)
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)

    children = defaultdict(list) # maps a node to its children

    def buildTree(node, parent):
        for adj in edgeMap[node]:
            if adj == parent:
                continue
            children[node].append(adj)
            buildTree(adj, node)
    buildTree(0, -1) # root at 0
    return children
    
class Solution:
    def minIncrease(self, n: int, edges: List[List[int]], cost: List[int]) -> int:

        children = edgeListToTree(edges)
        
        bigPath = -inf

        def dfs(node, above):
            nonlocal bigPath
            newPath = above + cost[node]
            if not children[node]:
                bigPath = max(bigPath, newPath)
            for child in children[node]:
                dfs(child, newPath)
        dfs(0, 0)

        # print(f'{bigPath=}')

        @cache
        def maxPath(node):
            if not children[node]:
                return cost[node]
            res = -inf
            for child in children[node]:
                res = max(res, cost[node] + maxPath(child))
            return res

        res = 0

        def dfs2(node, incAbove):
            nonlocal res
            maxBelowPath = maxPath(node)
            trueSum = incAbove + maxBelowPath
            newDiff = bigPath - trueSum
            if newDiff:
                res += 1
            for child in children[node]:
                dfs2(child, incAbove + newDiff + cost[node])
        dfs2(0, 0)

        return res