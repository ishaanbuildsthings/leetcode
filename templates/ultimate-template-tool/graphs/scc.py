# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/scc.py

# scc = buildScc(edges, numNodes, oneIndexed)
#   A strongly connected component is a group of nodes that can all reach each other
#   edges is a list of directed edges [[from, to], ...]; repeated edges and self-loops are fine
#   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
#   oneIndexed is True when the nodes are 1..numNodes, False when they're 0..numNodes-1
#   For example: buildScc([[1, 2], [2, 3], [3, 1], [4, 3]], 5, True)   (node 5 has no edges)
#
# scc.numComponents -> how many components there are, e.g. 3
#
# scc.nodeToComponentId[node] -> which component node is in, e.g. [-1, 0, 0, 0, 1, 2]
#   Component ids go from 0 to numComponents - 1. With oneIndexed, slot 0 isn't a node and is -1
#
# scc.componentNodes[componentId] -> that component's nodes, increasing, e.g. [[1, 2, 3], [4], [5]]
#
# scc.componentAdj[componentId] -> the components it has edges into, e.g. [[], [0], []]
#   Here component 1 (node 4) has an edge into component 0 (nodes 1, 2, 3). Edges inside a component are
#   dropped, repeats are kept, and following these never loops back
#
#   Ids come out in reverse topological order: every edge goes from a bigger id to a smaller one,
#   so going through ids 0, 1, 2, ... handles a component only after everything it can reach
#
# O(V + E) time and space


class Scc:
    def __init__(self, nodeToComponentId, componentNodes, componentAdj, numComponents):
        self.nodeToComponentId = nodeToComponentId
        self.componentNodes = componentNodes
        self.componentAdj = componentAdj
        self.numComponents = numComponents


def buildScc(edges, numNodes, oneIndexed: bool):
    if numNodes < 0:
        raise ValueError(f"buildScc: needs numNodes >= 0, got {numNodes}")
    firstNode = 1 if oneIndexed else 0
    lastNode = firstNode + numNodes - 1
    size = lastNode + 1
    adj = [[] for _ in range(size)]
    for a, b in edges:
        if not (firstNode <= a <= lastNode and firstNode <= b <= lastNode):
            raise ValueError(f"buildScc: edge ({a}, {b}) is outside the nodes {firstNode}..{lastNode}")
        adj[a].append(b)
    num = [0] * size
    low = [0] * size
    nodeToComponentId = [-1] * size
    onStk = [False] * size
    stk = []
    numComponents = 0
    timer = 0
    for start in range(firstNode, size):
        if num[start]:
            continue
        timer += 1
        num[start] = low[start] = timer
        stk.append(start)
        onStk[start] = True
        callStack = [[start, 0]]
        while callStack:
            frame = callStack[-1]
            node1, ei = frame
            if ei < len(adj[node1]):
                frame[1] += 1
                node2 = adj[node1][ei]
                if not num[node2]:
                    timer += 1
                    num[node2] = low[node2] = timer
                    stk.append(node2)
                    onStk[node2] = True
                    callStack.append([node2, 0])
                elif onStk[node2]:
                    low[node1] = min(low[node1], num[node2])
            else:
                if low[node1] == num[node1]:
                    while True:
                        node3 = stk.pop()
                        onStk[node3] = False
                        nodeToComponentId[node3] = numComponents
                        if node3 == node1:
                            break
                    numComponents += 1
                callStack.pop()
                if callStack:
                    parent = callStack[-1][0]
                    low[parent] = min(low[parent], low[node1])
    componentNodes = [[] for _ in range(numComponents)]
    componentAdj = [[] for _ in range(numComponents)]
    for node1 in range(firstNode, size):
        compId = nodeToComponentId[node1]
        componentNodes[compId].append(node1)
        for node2 in adj[node1]:
            if compId != nodeToComponentId[node2]:
                componentAdj[compId].append(nodeToComponentId[node2])
    return Scc(nodeToComponentId, componentNodes, componentAdj, numComponents)
