# https://leetcode.com/problems/all-paths-from-source-to-target/
# difficulty: medium
# tags: backtracking

# Problem
# Given a directed acyclic graph (DAG) of n nodes labeled from 0 to n - 1, find all possible paths from node 0 to node n - 1 and return them in any order.

# The graph is given as follows: graph[i] is a list of all nodes you can visit from node i (i.e., there is a directed edge from node i to node graph[i][j]).

# Solution, start at 0 and backtrack all paths. Our max stack depth is O(n) space, not sure time complexity

class Solution:
    def allPathsSourceTarget(self, graph: List[List[int]]) -> List[List[int]]:
        res = []
        def backtrack(node, currPath):
            # base case
            if node == len(graph) - 1:
                res.append([*currPath])
                return

            for adj in graph[node]:
                currPath.append(adj)
                backtrack(adj, currPath)
                currPath.pop()
        backtrack(0, [0])
        return res