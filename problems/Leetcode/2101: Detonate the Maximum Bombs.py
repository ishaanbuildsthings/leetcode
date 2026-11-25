# https://leetcode.com/problems/detonate-the-maximum-bombs/description/
# difficulty: medium
# tags: graph, directed, acyclic

# Problem
# You are given a list of bombs. The range of a bomb is defined as the area where its effect can be felt. This area is in the shape of a circle with the center as the location of the bomb.

# The bombs are represented by a 0-indexed 2D integer array bombs where bombs[i] = [xi, yi, ri]. xi and yi denote the X-coordinate and Y-coordinate of the location of the ith bomb, whereas ri denotes the radius of its range.

# You may choose to detonate a single bomb. When a bomb is detonated, it will detonate all bombs that lie in its range. These bombs will further detonate the bombs that lie in their ranges.

# Given the list of bombs, return the maximum number of bombs that can be detonated if you are allowed to detonate only one bomb.

# Solution
# Modeled as a DAG and found the biggest starting point. I'm not sure if there's something better in terms of running fewer DFS operations, like I think starting the DFS on nodes with an in-edge where we don't out-edge to them might be pointless

import math

class Solution:
    def maximumDetonation(self, bombs: List[List[int]]) -> int:
        edgeMap = defaultdict(list) # dag, maps index
        for i in range(len(bombs) - 1):
            for j in range(i + 1, len(bombs)):
                x1, y1, r1 = bombs[i]
                x2, y2, r2 = bombs[j]
                dist = math.sqrt(
                    abs(x1 - x2)**2 + abs(y1 - y2)**2
                )
                if dist <= r1:
                    edgeMap[i].append(j)
                if dist <= r2:
                    edgeMap[j].append(i)

        def count(node, seen):
            seen.add(node)
            currCount = 1

            for adj in edgeMap[node]:
                if adj in seen:
                    continue
                currCount += count(adj, seen)

            return currCount

        res = 0
        for startNode in range(len(bombs)):
            res = max(
                res,
                count(startNode, set())
            )
        return res
