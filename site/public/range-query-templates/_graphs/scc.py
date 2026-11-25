# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/scc.py

# Strongly connected components of a directed graph (iterative Tarjan): groups of nodes that can all reach each other.
# edges: [(a, b), ...] meaning a -> b; repeated edges and self-loops are fine.
# n, oneIndexed (both required): the nodes are 0..n-1, or 1..n when oneIndexed is True. The edges alone can't say this:
# a node with no edges never shows up in them, yet it's still a component by itself, so leaving it out would give
# the wrong count. And whether labels start at 0 or 1 decides which node is the missing one. Every edge must stay in
# that range.
#   scc = buildScc([(1, 2), (2, 3), (3, 1), (4, 3)], 5, oneIndexed=True)     # nodes 1..5; node 5 has no edges
#   scc = buildScc([(0, 1), (1, 0)], 3, oneIndexed=False)                     # nodes 0..2; node 2 has no edges
# The returned fields (node ids are your labels, component ids are 0..numComponents-1):
#   scc.numComponents       3
#   scc.nodeToComponentId   [-1, 0, 0, 0, 1, 2]       indexed by node (oneIndexed: slot 0 is unused, -1)
#   scc.componentNodes      [[1, 2, 3], [4], [5]]     indexed by component id, nodes increasing
#   scc.componentAdj        [[], [0], []]             indexed by component id: out-neighbor components (always acyclic);
#                                                     edges inside a component dropped, repeats kept
# Component ids come out in reverse topological order: every edge compA -> compB has compA > compB, so looping ids
# 0..numComponents-1 visits a component only after everything it can reach.
# O(V + E) time and space, V = n, E = number of edges


class Scc:
    def __init__(self, nodeToComponentId, componentNodes, componentAdj, numComponents):
        self.nodeToComponentId = nodeToComponentId
        self.componentNodes = componentNodes
        self.componentAdj = componentAdj
        self.numComponents = numComponents


def buildScc(edges, n, oneIndexed: bool):
    if n < 0:
        raise ValueError(f"buildScc: needs n >= 0, got {n}")
    firstNode = 1 if oneIndexed else 0
    lastNode = firstNode + n - 1
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
