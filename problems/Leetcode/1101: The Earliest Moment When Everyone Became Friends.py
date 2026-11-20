# https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/description/
# difficulty: medium
# tags: graphs, union find

# Problem
# There are n people in a social group labeled from 0 to n - 1. You are given an array logs where logs[i] = [timestampi, xi, yi] indicates that xi and yi will be friends at the time timestampi.

# Friendship is symmetric. That means if a is friends with b, then b is friends with a. Also, person a is acquainted with a person b if a is friends with b, or a is a friend of someone acquainted with b.

# Return the earliest time for which every person became acquainted with every other person. If there is no such earliest time, return -1.

# Solution
# Sort the queries and union find as needed. Need to look at path compression again.

class DSU:
    def __init__(self, n):
        self.parents = { node : node for node in range(n) }
        self.heights = { node : 1 for node in range(n) } # maps a representative parent to its height

    # finds the representative parent for a node and path compresses
    def find(self, node):
        if self.parents[node] == node:
            return node
        newParent = self.find(self.parents[node])
        self.parents[node] = newParent
        return newParent

    # unions two nodes and returns if the union was successful
    def union(self, a, b):
        aPar = self.find(a)
        bPar = self.find(b)
        if aPar == bPar:
            return False

        aHeight = self.heights[aPar]
        bHeight = self.heights[bPar]

        if aHeight <= bHeight:
            self.parents[aPar] = bPar
            del self.heights[aPar]
            if aHeight == bHeight:
                self.heights[bPar] += 1

        else:
            self.parents[bPar] = aPar
            del self.heights[bPar]

        return True

    def isConnected(self):
        return len(self.heights) == 1



class Solution:
    def earliestAcq(self, logs: List[List[int]], n: int) -> int:
        dsu = DSU(n)

        logs.sort()
        for log in logs:
            time, a, b = log
            dsu.union(a, b)
            if dsu.isConnected():
                return time

        return -1
