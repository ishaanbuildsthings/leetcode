# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# edgeList = [[a, b], [c, d], ...]
# roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label
# 0-indexed input -> children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
def edgeListToTree(edgeList, root):
    size = max(max(a, b) for a, b in edgeList) + 1
    edgeMap = [[] for _ in range(size)]
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)
    children = [[] for _ in range(size)]
    parent = [-1] * size
    stack = [root]
    while stack:
        node = stack.pop()
        for adj in edgeMap[node]:
            if adj == parent[node]:
                continue
            parent[adj] = node
            children[node].append(adj)
            stack.append(adj)
    return children

class Solution:
    def minCost(self, n: int, colors: str, edges: List[List[int]]) -> int:
        children = edgeListToTree(edges, 0) if edges else [[]]

        @cache
        def sz(node):
            return 1 + sum(sz(child) for child in children[node])

        # returns min cost for blue only, root red, contains red (root blue)
        @cache
        def dp(node):
            c = colors[node]
            if not children[node]:
                if c == 'R':
                    return (1, 0, inf)
                return (0, 1, inf)
        
            blueOnly = 0 if c == 'B' else sz(node)
            for child in children[node]:
                childBlue, childRedRoot, childContainRed = dp(child)
                blueOnly += childBlue
            
            redRoot = 0 if c == 'R' else sz(node)
            for child in children[node]:
                childBlue, childRedRoot, childContainRed = dp(child)
                redRoot += min(childRedRoot, childBlue)
            
            # only one child can contain red or be a red root, everything else will be blue
            childContainsRed = 0 if c == 'B' else sz(node)

            bests = []
            blues = []
            for child in children[node]:
                childBlue, childRedRoot, childContainRed = dp(child)
                bests.append(min(childRedRoot, childContainRed))
                blues.append(childBlue)
            
            totBlue = sum(blues)

            bestScore = inf

            for i in range(len(blues)):
                otherBlues = totBlue - blues[i]
                here = bests[i]
                score = otherBlues + here
                bestScore = min(bestScore, score)

            return (blueOnly, redRoot, childContainsRed + bestScore)
        
        return min(dp(0))
            





