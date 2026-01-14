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


def countEvenNodesAll(adjs, n):
    totalEven = [0] * n
    totalOdd = [0] * n
    res = [0] * n

    def dfs1(node, parent):
        totalEven[node] = 1
        totalOdd[node] = 0
        for adj in adjs[node]:
            if adj != parent:
                dfs1(adj, node)
                totalEven[node] += totalOdd[adj]
                totalOdd[node] += totalEven[adj]

    def dfs2(node, parent, upEven, upOdd):
        res[node] = totalEven[node] + upOdd
        for adj in adjs[node]:
            if adj != parent:
                nextUpEven = upOdd + totalOdd[node] - totalOdd[adj]
                nextUpOdd = upEven + totalEven[node] - totalEven[adj]
                dfs2(adj, node, nextUpEven, nextUpOdd)

    dfs1(0, -1)
    dfs2(0, -1, 0, 0)
    return res