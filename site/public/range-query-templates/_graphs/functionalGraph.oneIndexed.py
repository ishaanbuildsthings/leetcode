# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/functionalGraph.oneIndexed.py

# Functional graph breakdown, 1-indexed. In a functional graph every node has exactly one outgoing edge, so
# each component is exactly one cycle, with trees of tails feeding into it (several tails can enter the cycle,
# at different cycle nodes, and tails can branch).
# edges: [a, b] meaning a -> b, in any order. The nodes are 1..len(edges): there's one edge per node, so
# no node count is passed. Every node must be the start of exactly one edge, else it errors.
# Every per-node array is indexed by your labels; node 0 doesn't exist.
# Example (8 -> 8 is a self-loop, so it's a cycle of length 1):
#   fg = FunctionalGraph([(1, 2), (2, 3), (3, 4), (4, 2), (5, 3), (6, 5), (7, 1), (8, 8), (9, 8)])
#   fg.cycles() -> [[2, 3, 4], [8]]
#   fg.componentId(6) -> 0               fg.numEdgesToCrossBeforeCycle(6) -> 2      fg.firstCycleNodeHit(6) -> 3
#   fg.kthNext(6, 4) -> 2               (6 -> 5 -> 3 -> 4 -> 2)
#   fg.stepsFromTo(7, 4) -> 4           fg.stepsFromTo(5, 1) -> None  (5 never passes through 1)
#   fg.components() -> [([2, 3, 4], [[6, 5, 3], [7, 1, 2]]), ([8], [[9, 8]])]
# Build: O(V) time and space, V = number of nodes. Invalid nodes or a negative k raise ValueError.

from bisect import bisect_right


class FunctionalGraph:
    def __init__(self, edges):
        n = len(edges)
        size = n + 1
        self._n = n
        self._size = size
        nxt = [-1] * size
        for a, b in edges:
            if not (1 <= a < size and 1 <= b < size):
                raise ValueError(f"FunctionalGraph: edge ({a}, {b}) is outside the nodes 1..{size - 1} (one node per edge)")
            if nxt[a] != -1:
                raise ValueError(f"FunctionalGraph: node {a} is the start of more than one edge")
            nxt[a] = b
        # n edges, each node the start of at most one: so every node starts exactly one

        # find the cycles: walk forward from each unseen node until the walk hits something seen
        state = [0] * size  # 0 unseen, 1 on the current walk, 2 finished
        onCycle = [False] * size
        found = []
        for start in range(1, size):
            if state[start]:
                continue
            path = []
            node = start
            while state[node] == 0:
                state[node] = 1
                path.append(node)
                node = nxt[node]
            if state[node] == 1:  # the walk ran into itself: from there on it's a new cycle
                found.append(path[path.index(node):])
            for x in path:
                state[x] = 2
        cycles = []
        for cyc in found:
            m = cyc.index(min(cyc))
            cycles.append(cyc[m:] + cyc[:m])  # start at its smallest node
        cycles.sort()

        comp = [-1] * size
        depth = [0] * size  # edges to cross before being on a cycle
        first = [-1] * size  # first cycle node hit
        pos = [-1] * size  # index within its cycle, for cycle nodes
        for cid, cyc in enumerate(cycles):
            for i, node in enumerate(cyc):
                onCycle[node] = True
                comp[node] = cid
                first[node] = node
                pos[node] = i

        # the tails form trees hanging off cycle nodes: walk them backward, recording depth-first entry / exit times
        children = [[] for _ in range(size)]
        for a in range(1, size):
            if not onCycle[a]:
                children[nxt[a]].append(a)
        tin = [0] * size
        tout = [0] * size
        byDepthTins = []  # byDepthTins[d] = entry times of the nodes d edges from their cycle, increasing
        byDepthNodes = []
        timer = 0
        for cid, cyc in enumerate(cycles):
            for root in cyc:
                stack = [root]
                while stack:
                    node = stack.pop()
                    if node >= 0:
                        tin[node] = timer
                        timer += 1
                        d = depth[node]
                        if d == len(byDepthTins):
                            byDepthTins.append([])
                            byDepthNodes.append([])
                        byDepthTins[d].append(tin[node])
                        byDepthNodes[d].append(node)
                        stack.append(~node)
                        for child in children[node]:
                            depth[child] = d + 1
                            first[child] = first[node]
                            comp[child] = cid
                            stack.append(child)
                    else:
                        tout[~node] = timer - 1

        # components: each tail walk starts at a node nothing points to and stops at the first node already listed
        hasIncoming = [False] * size
        for a in range(1, size):
            hasIncoming[nxt[a]] = True
        listed = onCycle[:]
        components = [(cyc, []) for cyc in cycles]
        for start in range(1, size):
            if hasIncoming[start]:
                continue
            walk = [start]
            listed[start] = True
            node = nxt[start]
            while not listed[node]:
                walk.append(node)
                listed[node] = True
                node = nxt[node]
            walk.append(node)
            components[comp[start]][1].append(walk)

        self._nxt = nxt
        self._cycles = cycles
        self._comp = comp
        self._depth = depth
        self._first = first
        self._pos = pos
        self._tin = tin
        self._tout = tout
        self._byDepthTins = byDepthTins
        self._byDepthNodes = byDepthNodes
        self._components = components

    def _check(self, node):
        if not (1 <= node < self._size):
            raise ValueError(f"FunctionalGraph: node {node} is outside the nodes 1..{self._size - 1}")

    # O(1), every cycle as a list of only the nodes on it (no tails), in walking order: [1, 2, 3] is 1 -> 2 -> 3 -> 1.
    # Each starts at its smallest node; the cycles are sorted by that node. Its index here is its componentId
    def cycles(self):
        return self._cycles

    # O(1), which component node is in, for ANY node (on a cycle or not): an index into cycles(), 0..len(cycles()) - 1
    def componentId(self, node):
        self._check(node)
        return self._comp[node]

    # O(1), how many edges node crosses before being part of a cycle; 0 if node is on a cycle
    def numEdgesToCrossBeforeCycle(self, node):
        self._check(node)
        return self._depth[node]

    # O(1), the first cycle node node's walk reaches; a node on a cycle is its own
    def firstCycleNodeHit(self, node):
        self._check(node)
        return self._first[node]

    # O(1) if k reaches the cycle, else O(log V): where node is after k steps (k >= 0, any size). kthNext(node, 0) = node
    def kthNext(self, node, k):
        self._check(node)
        if k < 0:
            raise ValueError(f"FunctionalGraph: kthNext needs k >= 0, got {k}")
        d = self._depth[node]
        if k >= d:
            cyc = self._cycles[self._comp[node]]
            return cyc[(self._pos[self._first[node]] + k - d) % len(cyc)]
        # still on the tail: the node k steps ahead is the one at depth d - k whose subtree contains node, which is the
        # last node at that depth entered before node
        target = d - k
        i = bisect_right(self._byDepthTins[target], self._tin[node]) - 1
        return self._byDepthNodes[target][i]

    # O(1), how many steps it takes to get from a to b (0 if a == b), or None if a never reaches b
    def stepsFromTo(self, a, b):
        self._check(a)
        self._check(b)
        if self._comp[a] != self._comp[b]:
            return None
        if self._depth[b] == 0:  # b is on the cycle: reach the cycle, then go around to b
            cycLen = len(self._cycles[self._comp[b]])
            return self._depth[a] + (self._pos[b] - self._pos[self._first[a]]) % cycLen
        if self._tin[b] <= self._tin[a] <= self._tout[b]:  # b is on a tail: a has to come down through b
            return self._depth[a] - self._depth[b]
        return None

    # O(1) (built in O(V)), every component in componentId order as (cycle, tails):
    #   cycle = cycles()[componentId]
    #   tails = one walk per node with no incoming edges (increasing), following edges and stopping at the first node
    #           already listed (a cycle node, or a node of an earlier walk where the tails merge), which is included.
    #           Every node appears in the component once, plus each walk's last node. Total size O(V)
    def components(self):
        return self._components
