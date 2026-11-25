# https://leetcode.com/problems/paths-in-maze-that-lead-to-same-room/
# difficulty: medium
# tags: graph, undirected, cyclic

# Problem
# A maze consists of n rooms numbered from 1 to n, and some rooms are connected by corridors. You are given a 2D integer array corridors where corridors[i] = [room1i, room2i] indicates that there is a corridor connecting room1i and room2i, allowing a person in the maze to go from room1i to room2i and vice versa.

# The designer of the maze wants to know how confusing the maze is. The confusion score of the maze is the number of different cycles of length 3.

# For example, 1 → 2 → 3 → 1 is a cycle of length 3, but 1 → 2 → 3 → 4 and 1 → 2 → 3 → 2 → 1 are not.
# Two cycles are considered to be different if one or more of the rooms visited in the first cycle is not in the second cycle.

# Return the confusion score of the maze.

# Solution, I did a triple for loop, it may amortize based on the # of edges.

class Solution:
    def numberOfPaths(self, n: int, corridors: List[List[int]]) -> int:
        edgeMap = defaultdict(set)
        for a, b in corridors:
            edgeMap[a].add(b)
            edgeMap[b].add(a)

        res = 0

        # perhaps similar via amortization to iterate on each edge and for the two ending nodes doing a set intersection, not sure, but something is being amortized here

        for node in range(1, n + 1):
            for edge in edgeMap[node]:
                if edge < node:
                    continue
                for thirdEdge in edgeMap[edge]:
                    if thirdEdge < edge:
                        continue
                    res += thirdEdge in edgeMap[node]

        return res
