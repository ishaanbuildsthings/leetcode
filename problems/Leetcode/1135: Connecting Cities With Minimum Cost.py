# https://leetcode.com/problems/connecting-cities-with-minimum-cost/
# difficulty: medium
# algorithm: minimum spanning tree, union find, graphs

# Problem
# There are n cities labeled from 1 to n. You are given the integer n and an array connections where connections[i] = [xi, yi, costi] indicates that the cost of connecting city xi and city yi (bidirectional connection) is costi.

# Return the minimum cost to connect all the n cities such that there is at least one path between each pair of cities. If it is impossible to connect all the n cities, return -1,

# The cost is the sum of the connections' costs used.

# Solution, O(connections log connections time), O(n + sort(connections)) space
# Classic MST. Sort by cost, union the closest two if they aren't. Use path compression and union by rank.
class UnionFind:
    def __init__(self, size):
        self.parents = {} # initially all nodes point to themselves
        self.layers = {} # maps a representative cell to the number of its layers

        for node in range(1, size + 1):
            self.parents[node] = node
            self.layers[node] = 1

    # unions 2 nodes, or returns false if they were already unioned
    def union(self, a, b):
        parentA = self.find(a)
        parentB = self.find(b)
        if parentA == parentB:
            return False

        layersA = self.layers[parentA]
        layersB = self.layers[parentB]
        if layersB > layersA:
            parentB, parentA = parentA, parentB # make B always <= A
        self.parents[parentB] = parentA
        if layersA == layersB:
            self.layers[parentA] += 1
        del self.layers[parentB]
        return True

    # finds the parent for a node
    def find(self, a):
        if self.parents[a] == a:
            return a
        self.parents[a] = self.find(self.parents[a])
        return self.parents[a]

class Solution:
    def minimumCost(self, n: int, connections: List[List[int]]) -> int:
        connections.sort(key=lambda x: x[2])
        dsu = UnionFind(n)

        edgesAdded = 0
        totalCost = 0
        for a, b, cost in connections:
            if edgesAdded == n - 1:
                return totalCost
            if dsu.union(a, b):
                edgesAdded += 1
                totalCost += cost
        if edgesAdded == n - 1:
            return totalCost

        return -1 # we couldn't union everything


