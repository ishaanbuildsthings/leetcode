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




# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/compress/template.py
# @operations: areUnioned elementsInGroup find groups largestSize numComponents roots size sizes unite
# @data-structure-type: dsu
# @complexities:
#   areUnioned: α(N) amortized
#   elementsInGroup: N
#   find: α(N) amortized
#   groups: N
#   largestSize: 1
#   numComponents: 1
#   roots: N
#   size: α(N) amortized
#   sizes: N*log(N)
#   unite: α(N) amortized
#   build: N
# @memory:
#   layout: none
#   node: par[1*N] sz[1*N]
#   tags: none
#   other: vals[1*N]

# dsu = DSU(vals)
# vals: the elements (any values: numbers, strings, tuples, ...); everything works on their indices 0..n-1


class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0

    # O(α(n)) amortized, effectively O(1): index of the representative of i's component
    def find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(α(n)) amortized, merges the two components, False if i and j were already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return False
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        if self.sz[i] > self.mx:
            self.mx = self.sz[i]
        return True

    # O(α(n)) amortized, True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(α(n)) amortized, how many elements are in i's component
    def size(self, i):
        return self.sz[self.find(i)]

    # O(1), how many components exist right now
    def numComponents(self):
        return self.comps

    # O(1), size of the biggest component, maintained in unite
    def largestSize(self):
        return self.mx

    # O(n), one index per component: the representative each member's find returns
    def roots(self):
        return [i for i in range(len(self.par)) if self.par[i] == i]

    # O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    def sizes(self):
        return sorted((self.sz[i] for i in range(len(self.par)) if self.par[i] == i), reverse=True)

    # O(n), groupsArr[rt] = list of values whose root is rt, [] if rt is not a root
    def groups(self):
        n = len(self.par)
        groupsArr = [[] for _ in range(n)]
        for i in range(n):
            groupsArr[self.find(i)].append(self.vals[i])
        return groupsArr

    # O(n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]




t = int(input())

def solve():
    n, m = map(int, input().split())
    g = [[] for _ in range(n)] # g[node] -> [(adjN, w), ...]
    dsu = DSU(list(range(n)))
    for i in range(m):
        a, b, w = map(int, input().split())
        a -= 1
        b -= 1
        g[a].append((b, w))
        g[b].append((a, w))
        dsu.unite(a, b)
    
    groupArr = dsu.groups()

    res = 0

    for group in groupArr:
        if not group:
            continue
        # print('------')
        # print(f'processing group: {group}')

        s = sorted(group)
        nodeToLeft = {} # maps a raw node val to its left node idx WITH STRINGS
        for i, node in enumerate(s):
            nodeToLeft[str(node)] = i
        
        nodeToRight = {}
        for i, node in enumerate(s):
            nodeToRight[str(node)] = i + len(s)
        
        # print(f'{nodeToLeft=}')
        # print(f'{nodeToRight=}')

        edges = []

        gset = set()
        for v in group:
            gset.add(str(v))

        for node in group:
            for b, w in g[node]:
                if str(b) not in gset:
                    continue
                if w == 2:
                    edges.append((nodeToLeft[str(node)], nodeToRight[str(b)]))
                    edges.append((nodeToLeft[str(b)], nodeToRight[str(node)]))
                else:
                    edges.append((nodeToRight[str(node)], nodeToLeft[str(b)]))
                    edges.append((nodeToRight[str(b)], nodeToLeft[str(node)]))
        
        scc = buildScc(edges, len(group) * 2, False)
        if scc.numComponents == 2 * len(group):
            continue
        res += 1
    
    print(res)


        # all black edges go right, both directions

        # g2 = defaultdict(list) # directed, goes from 0...n-1 and n...2n-1, maps node -> other edge

        # for node in group:
        #     for b, w in g[node]:
        #         g2[node].a


for _ in range(t):
    solve()