# https://leetcode.com/problems/find-center-of-star-graph/description/
# difficulty: easy
# tags: graphs

# Problem
# There is an undirected star graph consisting of n nodes labeled from 1 to n. A star graph is a graph where there is one center node and exactly n - 1 edges that connect the center node with every other node.

# You are given a 2D integer array edges where each edges[i] = [ui, vi] indicates that there is an edge between the nodes ui and vi. Return the center of the given star graph.

# Solution, O(n) time and space, iterate until we find a repeated edge
# Technically, this solution is O(1) time and space because after the second edge it will always terminate, as the center is part of every edge. I wasn't really thinking when I wrote this though...

class Solution:
    def findCenter(self, edges: List[List[int]]) -> int:
        seen = set()
        for a, b in edges:
            if a in seen:
                return a
            if b in seen:
                return b
            seen.add(a)
            seen.add(b)