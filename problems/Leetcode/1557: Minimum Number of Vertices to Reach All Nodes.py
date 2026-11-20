# https://leetcode.com/problems/minimum-number-of-vertices-to-reach-all-nodes/description/
# difficulty: medium
# tags: graphs

# Problem
# Given a directed acyclic graph, with n vertices numbered from 0 to n-1, and an array edges where edges[i] = [fromi, toi] represents a directed edge from node fromi to node toi.

# Find the smallest set of vertices from which all nodes in the graph are reachable. It's guaranteed that a unique solution exists.

# Notice that you can return the vertices in any order.

# Solution
# Standard topological sort esque thinking, I realized we just track nodes with an indegree of 0.

class Solution:
    def findSmallestSetOfVertices(self, n: int, edges: List[List[int]]) -> List[int]:
        edgeMap = {
            node : []
            for node in range(n)
        }

        for a, b in edges:
            edgeMap[b].append(a)
        return [edge for edge in edgeMap if len(edgeMap[edge]) == 0]
        # for

        #    4
        #    v \
        # 0<-1->2
        #    v
        #    3


        #    0,2,3