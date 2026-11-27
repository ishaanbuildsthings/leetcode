# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/functionalGraph.py

# fg = FunctionalGraph(edges)
#   edges is a list of directed edges [[from, to], ...], with exactly one edge leaving
#   each node, so the nodes are 0..len(edges)-1 (it errors otherwise)
#
# fg.cycles() -> a list of every cycle, e.g. [[1, 3, 9], [2], [4, 10]]
#   Only nodes inside cycles, never the nodes on tails leading into them. Each cycle is in walking
#   order (1 -> 3 -> 9 -> 1) and starts at its smallest node. Here 2 points to itself
#
# fg.componentId(node) -> which component node is in, e.g. 1
#   Works for every node, on a cycle or not. It's an index into fg.cycles(), from 0 up to
#   len(fg.cycles()) - 1. So a node can have componentId 0 and be in the 0th cycle's
#   component without being on that cycle itself
#
# fg.numEdgesToCrossBeforeCycle(node) -> edges node crosses before it's inside a cycle, e.g. 2
#   0 if node is already on a cycle
#
# fg.firstCycleNodeHit(node) -> the first cycle node that node reaches, e.g. 3
#   node itself if it's already on a cycle
#
# fg.kthNext(node, k) -> the node you land on after k steps from node, e.g. 9
#   Any k >= 0, even 10^18. kthNext(node, 0) is node
#
# fg.stepsFromTo(a, b) -> how many steps it takes to walk from a to b, e.g. 4
#   None if a never reaches b, 0 if a == b
#
# fg.components() -> the full structure of the cycles and their tails
#   Returns one (cycle, tails) per component, in componentId order, e.g.
#   [([1, 3, 9], [[5, 6, 3], [7, 3]]), ([2], [[0, 2]]), ([4, 10], [[8, 4]])]
#
#   First comes the cycle, exactly as fg.cycles() gives it: [1, 3, 9]
#
#   Then the list of tails. A tail is a walk starting at a node nothing points to, following edges
#   until it hits a cycle node, which is included. Above, the first cycle is 1 -> 3 -> 9 and two
#   tails feed into it, both entering at 3: [5, 6, 3] is 5 -> 6 -> 3 and [7, 3] is 7 -> 3
#
#   If a tail runs into an earlier tail before reaching the cycle, it stops at that node instead,
#   so no node is listed twice: with one more edge 11 -> 6, its tail would be [11, 6]
#
# Build O(V) time and space. Every method is O(1) except kthNext, which is O(log V) when k
# stops before reaching the cycle. Invalid nodes or a negative k raise ValueError

from bisect import bisect_right


class FunctionalGraph:
    def __init__(self, edges):
        n = len(edges)
        size = n + 0
        self._n = n
        self._size = size
        nxt = [-1] * size
        for a, b in edges:
            if not (0 <= a < size and 0 <= b < size):
                raise ValueError(f"FunctionalGraph: edge ({a}, {b}) is outside the nodes 0..{size - 1} (one node per edge)")
            if nxt[a] != -1:
                raise ValueError(f"FunctionalGraph: node {a} is the start of more than one edge")
            nxt[a] = b
        # n edges, each node the start of at most one: so every node starts exactly one

        # find the cycles: walk forward from each unseen node until the walk hits something seen
        state = [0] * size  # 0 unseen, 1 on the current walk, 2 finished
        onCycle = [False] * size
        found = []
        for start in range(0, size):
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
        for a in range(0, size):
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
        for a in range(0, size):
            hasIncoming[nxt[a]] = True
        listed = onCycle[:]
        components = [(cyc, []) for cyc in cycles]
        for start in range(0, size):
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
        if not (0 <= node < self._size):
            raise ValueError(f"FunctionalGraph: node {node} is outside the nodes 0..{self._size - 1}")

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
