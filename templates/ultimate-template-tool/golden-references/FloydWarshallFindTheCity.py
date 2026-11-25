# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/FloydWarshallFindTheCity.py
# Floyd-Warshall as a full solution to LeetCode 1334 "Find the City With the Smallest Number of Neighbors at a Threshold Distance"
# (https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/).
# minDist(a, b, k) is the shortest a -> b route whose middle stops are all in cities 0..k: either the route avoids city k,
# or it goes through k once, splitting into a -> k and k -> b, neither of which needs k as a middle stop.
# Time O(V^3), space O(V^3) for the cache (a bottom-up table is O(V^2)).
from collections import defaultdict
from functools import cache
from math import inf
from typing import List

class Solution:
    def findTheCity(self, n: int, edges: List[List[int]], distanceThreshold: int) -> int:

        edgeMp = defaultdict(lambda : inf) # maps (a, b) -> minDist
        for a, b, w in edges:
            edgeMp[a, b] = min(edgeMp[a, b], w)
            edgeMp[b, a] = min(edgeMp[b, a], w)

        @cache
        def minDist(a, b, k):
            if a == b:
                return 0
            if k == -1:
                return edgeMp[a, b]
            
            avoidK = minDist(a, b, k - 1)
            throughK = minDist(a, k, k - 1) + minDist(k, b, k - 1)
            return min(avoidK, throughK)
        
        reach = [0] * n
        for node in range(n):
            for target in range(n):
                dist = minDist(node, target, n - 1)
                if dist <= distanceThreshold:
                    reach[node] += 1
        mn = min(reach)
        for i in range(n - 1, -1, -1):
            if reach[i] == mn:
                return i
