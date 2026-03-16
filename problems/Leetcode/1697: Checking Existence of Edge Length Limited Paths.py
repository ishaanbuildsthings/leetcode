# https://leetcode.com/problems/checking-existence-of-edge-length-limited-paths/submissions/1112397012/
# difficulty: hard
# tags: graphs, union find, offline

# Problem
# An undirected graph of n nodes is defined by edgeList, where edgeList[i] = [ui, vi, disi] denotes an edge between nodes ui and vi with distance disi. Note that there may be multiple edges between two nodes.

# Given an array queries, where queries[j] = [pj, qj, limitj], your task is to determine for each queries[j] whether there is a path between pj and qj such that each edge on the path has a distance strictly less than limitj .

# Return a boolean array answer, where answer.length == queries.length and the jth value of answer is true if there is a path for queries[j] is true, and false otherwise.

# Solution, since the queries are offline, we can just union edges in order

class DSU:
    def __init__(self, n):
        self.parents = {} # maps a node to SOME parent, depends on the current amount of path compression, doesn't always map directly to the representative parent, may need to follow a chain
        self.depths = {} # maps the representative parent to its depth
        for node in range(n):
            self.parents[node] = node
            self.depths[node] = 1

    # finds the representative parent for a node and path compresses
    def _find(self, node):
        # base case
        if self.parents[node] == node:
            return node

        while self.parents[node] != node:
            parent = self.parents[node]
            doubleParent = self.parents[parent]
            self.parents[node] = doubleParent
            node = doubleParent
        return node

    # unions two nodes, returns true/false inf successful
    def union(self, a, b):
        aRepParent = self._find(a)
        bRepParent = self._find(b)
        # if they are the same, they are already unioned
        if aRepParent == bRepParent:
            return False

        aDepth = self.depths[aRepParent]
        bDepth = self.depths[bRepParent]
        # bring a under b
        if aDepth < bDepth:
            self.parents[aRepParent] = bRepParent
            del self.depths[aRepParent]
        elif bDepth < aDepth:
            self.parents[bRepParent] = aRepParent
            del self.depths[bRepParent]
        else:
            self.parents[aRepParent] = bRepParent
            del self.depths[aRepParent]
            self.depths[bRepParent] += 1
        return True

    def areUnioned(self, a, b):
        return self._find(a) == self._find(b)


class Solution:
    def distanceLimitedPathsExist(self, n: int, edgeList: List[List[int]], queries: List[List[int]]) -> List[bool]:
        dsu = DSU(n)
        edgeList.sort(key=lambda edge: edge[2])

        zipped = list(enumerate(queries))
        zipped.sort(key=lambda tup: tup[1][2])

        nextEdge = 0

        res = [None] * len(queries)

        for tup in zipped:
            originalQueryI, query = tup
            a, b, limit = query
            limit -= 1 # strictly greater than conversion to <=
            while nextEdge < len(edgeList) and edgeList[nextEdge][2] <= limit:
                edge = edgeList[nextEdge]
                node1, node2, _ = edge
                dsu.union(node1, node2)
                nextEdge += 1
            res[originalQueryI] = dsu.areUnioned(a, b)

        return res


