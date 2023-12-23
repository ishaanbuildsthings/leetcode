# https://leetcode.com/problems/min-cost-to-connect-all-points/description/
# difficulty: medium
# tags: graphs, minimum spanning tree, union find

# Problem
# You are given an array points representing integer coordinates of some points on a 2D-plane, where points[i] = [xi, yi].

# The cost of connecting two points [xi, yi] and [xj, yj] is the manhattan distance between them: |xi - xj| + |yi - yj|, where |val| denotes the absolute value of val.

# Return the minimum cost to make all points connected. All points are connected if there is exactly one simple path between any two points.

# O(n^2 * log n) time, O(sort(n^2) + n) space
# Solution, for each pair of points, create a potential edge, then sort them by distance. Now for potential edge, if they're not unioned, we should union them which we consider constant time due to the inverse ackermann function. We stop when we have n - 1 edges, as that's the minimum number of edges needed to connect all points. I should add more intuition about why this works, though I think the intuition about greedily adding the closest point for a given node unless already unioned is related.

class UnionFind:
    def __init__(self, size): # assumes all nodes are numbered 0 to n-1 and we number the nodes when we sort
        self.parents = {} # maps a cell to its parent, a root points to itself
        for i in range(size):
            self.parents[i] = i
        self.ranks = {}
        for i in range(size): # maps a parent / representative cell to its group size
            self.ranks[i] = 0

    # finds the parent of a node and compresses the path
    def findParent(self, node):
        if self.parents[node] != node:
            self.parents[node] = self.findParent(self.parents[node])
        return self.parents[node]

    # unions two cells with an edge, or return false if no edge was added (they're already unioned)
    def union(self, node1, node2):
        parent1 = self.findParent(node1)
        parent2 = self.findParent(node2)

        # if they have the same parent, they're already unioned
        if parent1 == parent2:
            return False

        # union by rank, a smaller tree should join as a child of a larger one
        rank1 = self.ranks[parent1]
        rank2 = self.ranks[parent2]
        # if the first tree is smaller, it should union to the bigger one
        if rank1 < rank2:
            self.parents[parent1] = parent2
            del self.ranks[parent1]
        elif rank1 > rank2:
            self.parents[parent2] = parent1
            del self.ranks[parent2]
        # if the same, union and increase size
        else:
            self.parents[parent1] = parent2
            del self.ranks[parent1]
            self.ranks[parent2] += 1

        return True


class Solution:
    def minCostConnectPoints(self, points: List[List[int]]) -> int:
        edges = [] # holds [dist, point1num, point2num]
        # create n^2 possible edges
        for currNodeNum in range(len(points) - 1):
            for nextNodeNum in range(currNodeNum + 1, len(points)):
                point1 = points[currNodeNum]
                point2 = points[nextNodeNum]
                dist = abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
                edges.append([dist, currNodeNum, nextNodeNum])
        edges.sort()
        dsu = UnionFind(len(points))

        edgesAdded = 0
        edgesNeeded = len(points) - 1
        result = 0
        for edge in edges:
            if edgesAdded == edgesNeeded:
                return result
            dist, point1num, point2num = edge
            if dsu.union(point1num, point2num):
                result += dist
                edgesAdded += 1
        return result # in case final union gave result, for two points

