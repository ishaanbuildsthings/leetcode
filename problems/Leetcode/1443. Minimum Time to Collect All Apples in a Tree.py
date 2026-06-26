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
    def minTime(self, n: int, edges: List[List[int]], hasApple: List[bool]) -> int:
        children = edgeListToTree(edges)
        @cache
        def contains(node):
            if hasApple[node]:
                return True
            for child in children[node]:
                if contains(child):
                    return True
            return False
        
        def dfs(node):
            if not children[node]:
                return 0
            res = 0
            for child in children[node]:
                if contains(child):
                    res += 2 + dfs(child)
            return res
        
        return dfs(0)