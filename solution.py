from typing import List, Dict, Tuple, Set, Optional, Union, Any
import math
import bisect
import collections
from collections import defaultdict, Counter
import sortedcontainers
import heapq
from heapq import nlargest, nsmallest


# PREPROCESSING OR TEMPLATES GO HERE



testcases = [
'Input: n = 3, maxDistance = 5, roads = [[0,1,2],[1,2,10],[0,2,10]]',
'Input: n = 3, maxDistance = 5, roads = [[0,1,2],[1,2,10],[0,2,10]]'
]

expectedResults = [
2,
5
]

class Solution:
    def numberOfSets(self, n: int, maxDistance: int, roads: List[List[int]]) -> int:
        _inner = lambda: defaultdict(lambda: float('inf'))
        edgeMap = defaultdict(_inner) # maps node to another node to the smallest edge weight

        for a, b, weight in roads:
            edgeMap[a][b] = min(edgeMap[a][b], weight)
            edgeMap[b][a] = min(edgeMap[b][a], weight)

        # print(f'init edge map: {edgeMap}')

        res = 0

        def isMaskDoable(mask):
            # FLOYD WARSHALL
            distance = [[float('inf')] * n for _ in range(n)]

            # populate with init distances
            for i in range(n):
                # skip closed branches
                if mask & (1 << i):
                    continue
                # set identity distance
                distance[i][i] = 0
                # iterate over adjacent nodes
                for j in edgeMap[i].keys():
                    # skip adjacent closed ones
                    if mask & (1 << j):
                        continue
                    # set initial edge
                    distance[i][j] = edgeMap[i][j]

            # allow us to use up to 0, 1, 2, ... k as our midpoint
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        # if either is closed skip those, we cannot use them
                        if mask & (1 << i) or mask & (1 << j):
                            continue
                        distance[i][j] = min(distance[i][j], distance[i][k] + distance[k][j])

            # check every pair
            for i in range(n):
                for j in range(n):
                    if mask & (1 << i) or mask & (1 << j):
                        continue
                    if distance[i][j] > maxDistance:
                        return False
            return True

        res = 0
        for mask in range(1 << n):
            res += isMaskDoable(mask)
        return res

