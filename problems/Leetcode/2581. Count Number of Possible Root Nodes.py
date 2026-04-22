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
    def rootCount(self, edges: List[List[int]], guesses: List[List[int]], k: int) -> int:
        children = edgeListToTree(edges)
        guessSet = set(tuple(g) for g in guesses) # parent, child
        n = len(edges) + 1
        down = [0] * n # how many true relations exist in this subtree

        def dfs1(node):
            resHere = 0
            for child in children[node]:
                if (node, child) in guessSet:
                    resHere += 1
                dfs1(child)
                resHere += down[child]
            down[node] = resHere
        
        dfs1(0)

        full = [0] * n # when rooted here, how many do we get
        full[0] = down[0]

        def dfs2(node):
            for child in children[node]:
                resHere = full[node]
                if (child, node) in guessSet:
                    resHere += 1
                if (node, child) in guessSet:
                    resHere -= 1
                full[child] = resHere
                dfs2(child)
        
        dfs2(0)

        return sum(1 if x >= k else 0 for x in full)


