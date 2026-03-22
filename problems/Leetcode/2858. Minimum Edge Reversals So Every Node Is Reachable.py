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
    def minEdgeReversals(self, n: int, edges: List[List[int]]) -> List[int]:
        adj = defaultdict(dict) # adj[node1][node2] tells us cost to travel
        for a, b in edges:
            adj[a][b] = 0
            adj[b][a] = 1
        
        # undirected
        children = edgeListToTree(edges)

        arr1 = [0] * n

        # tells us how mant reversals needed to make entire subtree reachable
        def dfs1(node):
            if not children[node]:
                return
            resHere = 0
            for child in children[node]:
                dfs1(child)
                resHere += arr1[child]
                resHere += adj[node][child]
            arr1[node] = resHere
        
        dfs1(0)

        res = [0] * n
        res[0] = arr1[0]
        
        # reroot here
        def dfs2(node):
            for child in children[node]:
                rootReach = res[node]
                rootReach -= adj[node][child]
                rootReach += adj[child][node]
                res[child] = rootReach
                dfs2(child)
        
        dfs2(0)

        return res

        

        
        