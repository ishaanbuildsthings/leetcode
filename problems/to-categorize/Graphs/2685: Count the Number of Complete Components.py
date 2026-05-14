# https://leetcode.com/problems/count-the-number-of-complete-components/
# difficulty: medium
# tags: graph

# Problem
# You are given an integer n. There is an undirected graph with n vertices, numbered from 0 to n - 1. You are given a 2D integer array edges where edges[i] = [ai, bi] denotes that there exists an undirected edge connecting vertices ai and bi.

# Return the number of complete connected components of the graph.

# A connected component is a subgraph of a graph in which there exists a path between any two vertices, and no vertex of the subgraph shares an edge with a vertex outside of the subgraph.

# A connected component is said to be complete if there exists an edge between every pair of its vertices.

# Solution
# I am writing this way after I solved the problem so I don't remember exactly how I did it. Seems like I track all nodes ever seen, recurse, and deduce information. I remember a few strategies not working for this so you have to think about it more deeply.

class Solution:
    def countCompleteComponents(self, n: int, edges: List[List[int]]) -> int:
        edgeMap = defaultdict(list)
        for a, b in edges:
            edgeMap[a].append(b)
            edgeMap[b].append(a)

        visitedCount = set()
        def dfsCount(node, accNodes):
            visitedCount.add(node)
            accNodes.append(node)
            for neighbor in edgeMap[node]:
                if neighbor in visitedCount:
                    continue
                dfsCount(neighbor, accNodes)
            return accNodes

        res = 0
        for node in range(n):
            # already did this component before
            if node in visitedCount:
                continue
            sizePre = len(visitedCount)
            accNodes = dfsCount(node, [])
            sizePost = len(visitedCount)
            wrongSizeFound = False
            for accNode in accNodes:
                if len(edgeMap[accNode]) != (sizePost - sizePre) - 1:
                    wrongSizeFound = True
                    break
            if not wrongSizeFound:
                res += 1
        return res


