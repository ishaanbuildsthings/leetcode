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
    def maxSubgraphScore(self, n: int, edges: List[List[int]], good: List[int]) -> List[int]:
        children = edgeListToTree(edges)

        good = [1 if x else -1 for x in good]
        down = [0] * n

        def dfs1(node):
            if not children[node]:
                down[node] = good[node]
                return
            resHere = good[node]
            for child in children[node]:
                dfs1(child)
                bst = max(0, down[child])
                resHere += bst
            down[node] = resHere
        
        dfs1(0)

        full = [0] * n
        full[0] = down[0]
        def dfs2(node):
            for child in children[node]:
                fbest = full[node]
                fbest -= max(0, down[child])
                fbest = max(fbest, 0)
                fbest += down[child]
                full[child] = fbest
                dfs2(child)
        dfs2(0)
        return full

