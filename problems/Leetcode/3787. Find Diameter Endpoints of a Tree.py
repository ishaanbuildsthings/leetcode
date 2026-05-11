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
    def findSpecialNodes(self, n: int, edges: List[List[int]]) -> str:

        children = edgeListToTree(edges)

        diameter = 0
        # bubbble up max depth
        def dfs(node):
            nonlocal diameter
            if not children[node]:
                return 1
            childs = [dfs(child) for child in children[node]]
            childs.sort(reverse=True)
            maxDiam = childs[0]
            if len(childs) > 1:
                maxDiam += childs[1]
            diameter = max(diameter, maxDiam)
            return childs[0] + 1
        
        dfs(0)
        
        # first assume we know the diameter

        # idea 1: O(n)
        # reroot dp, check if every node can be a diameter

        # idea 2: O(n log n)
        # centroid decomposition
        # enumerate paths on centroids to check longest

        removed = [False] * n
        sizes = [0] * n
        touched = []

        resSet = set()

        adj = defaultdict(list)
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        distCnt = Counter() # maps distance -> count of distances

        def subtreeSize(node, parent):
            sizeHere = 1
            for adjN in adj[node]:
                if adjN == parent: continue
                if removed[adjN]: continue
                subtreeSize(adjN, node)
                sizeHere += sizes[adjN]
            sizes[node] = sizeHere

        def findCentroid(node, parent, pieceSize):
            mxChild = 0
            heavyChild = -1
            for adjN in adj[node]:
                if adjN == parent: continue
                if removed[adjN]: continue
                if sizes[adjN] > mxChild:
                    mxChild = sizes[adjN]
                    heavyChild = adjN
            
            if mxChild <= pieceSize / 2:
                return node
            
            return findCentroid(heavyChild, node, pieceSize)
        
        def pickup(node, parent, currDist):
            touched.append(currDist)
            distCnt[currDist] += 1
            for adjN in adj[node]:
                if adjN == parent: continue
                if removed[adjN]: continue
                pickup(adjN, node, currDist + 1)
        
        def drop(node, parent, currDist):
            distCnt[currDist] -= 1
            for adjN in adj[node]:
                if adjN == parent: continue
                if removed[adjN]: continue
                drop(adjN, node, currDist + 1)
            
        def score(node, parent, currDist):
            reqDist = diameter - currDist
            if distCnt[reqDist]:
                resSet.add(node)
            for adjN in adj[node]:
                if adjN == parent: continue
                if removed[adjN]: continue
                score(adjN, node, currDist + 1)

        def decompose(entry):
            # 1 compute sizes
            subtreeSize(0, -1)
            size = sizes[entry]

            distCnt[0] = 1

            # 2 find centroid
            centroid = findCentroid(entry, -1, size)

            # 3 do some work
            for adjN in adj[centroid]:
                if removed[adjN]: continue
                pickup(adjN, centroid, 1)
                        
            for adjN in adj[centroid]:
                if removed[adjN]: continue
                drop(adjN, centroid, 1)
                score(adjN, centroid, 1)
                pickup(adjN, centroid, 1)

            # 4 remove centroid
            removed[centroid] = True
            for v in touched:
                if v == diameter:
                    resSet.add(centroid)
                distCnt[v] = 0
            while touched:
                touched.pop()

            # 5 recurse
            for adjN in adj[centroid]:
                if removed[adjN]: continue
                decompose(adjN)
        
        decompose(0)

        resArr = []
        for node in range(n):
            if node in resSet:
                resArr.append('1')
            else:
                resArr.append('0')

        return ''.join(resArr)            


