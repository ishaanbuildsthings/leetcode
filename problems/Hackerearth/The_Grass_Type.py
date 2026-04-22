import sys
from collections import Counter
data = list(map(int, sys.stdin.buffer.read().split()))
 
n = data[0] # number of vertices
edgeStart = 1
edgeEnd = edgeStart + 2*(n - 1)
 
edges = [(data[i], data[i + 1]) for i in range(edgeStart, edgeEnd, 2)]
 
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
    buildTree(1, -1) # root at 1
    return children
children = edgeListToTree(edges)
 
labels = data[edgeEnd: edgeEnd + n]
 
# print(labels)
# print(f'{children=}')
 
res = 0
def dfs(node):
    global res
    bigC = Counter()
    goalValue = labels[node-1]
    for child in children[node]:
        childC = dfs(child)
        if len(childC) > len(bigC):
            bigC, childC = childC, bigC
        for childLabel in childC:
            if goalValue % childLabel == 0:
                complement = goalValue // childLabel
                countOfComplement = bigC[complement // 1]
                countInHere = childC[childLabel]
                res += countOfComplement * countInHere
        for childLabel in childC:
            bigC[childLabel] += childC[childLabel]
    complementWithRoot = bigC[1]
    res += complementWithRoot
    bigC[goalValue] += 1
    return bigC
 
dfs(1)
 
print(res)