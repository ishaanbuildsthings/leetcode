# Template by ishaanbuildsthings (github.com/ishaanbuildsthings)
#
# adj is a list of out-neighbor lists, indexed by node id in [0, n), directed.
# Every index is a real node — convert 1-indexed input before calling.
#   adj = [[1], [2], [0], [2]]          # edges 0->1, 1->2, 2->0, 3->2
scc = buildScc(adj)                     # O(n + m) time and space
#
# A component is a maximal group of nodes that can all reach each other. Here
# {0,1,2} is one (the cycle 0->1->2->0) and {3} is the other.
#
# scc.numComponents      int, the number of components C
#   2
#
# scc.nodeToComponentId  list[int], indexed by node id -> its component id, O(1)
#   [0, 0, 0, 1]                        # nodes 0,1,2 -> comp 0;  node 3 -> comp 1
#
# scc.componentNodes     list[list[int]], indexed by component id -> its nodes, O(1)
#   [[0, 1, 2], [3]]
#
# scc.componentAdj       list[list[int]], indexed by component id -> out-neighbor
#                        component ids. Always acyclic. Intra-component edges dropped;
#                        duplicates kept when several edges cross the same pair. O(1)
#   [[], [0]]                           # original edge 3->2 became comp 1 -> comp 0
#
# Component ids come out in reverse topological order: every edge compA -> compB has
# compA > compB, so looping ids 0..C-1 visits a component only after all it can reach.
class Scc:
    def __init__(self, nodeToComponentId, componentNodes, componentAdj, numComponents):
        self.nodeToComponentId = nodeToComponentId
        self.componentNodes = componentNodes
        self.componentAdj = componentAdj
        self.numComponents = numComponents


def buildScc(adj):
    n = len(adj)
    num = [0] * n
    low = [0] * n
    nodeToComponentId = [-1] * n
    onStk = [False] * n
    stk = []
    numComponents = 0
    timer = 0

    for start in range(n):
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
    for node1 in range(n):
        compId = nodeToComponentId[node1]
        componentNodes[compId].append(node1)
        for node2 in adj[node1]:
            if compId != nodeToComponentId[node2]:
                componentAdj[compId].append(nodeToComponentId[node2])
    return Scc(nodeToComponentId, componentNodes, componentAdj, numComponents)