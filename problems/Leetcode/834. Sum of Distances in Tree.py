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
    def sumOfDistancesInTree(self, N, edges):
        children = edgeListToTree(edges)

        @cache
        def cnt(node):
            if not children[node]:
                return 1
            return 1 + sum(cnt(child) for child in children[node])
        
        down = [0] * N

        def dfs1(node):
            resHere = 0
            for child in children[node]:
                dfs1(child)
                totToChild = down[child]
                childCnt = cnt(child)
                resHere += totToChild
                resHere += childCnt
            down[node] = resHere
        
        dfs1(0)

        full = [0] * N
        full[0] = down[0]

        def dfs2(node):
            for child in children[node]:
                parentDistances = full[node]
                childCnt = cnt(child)
                parentDistances -= childCnt
                parentDistances += N - childCnt
                full[child] = parentDistances
                dfs2(child)
        
        dfs2(0)

        return full

