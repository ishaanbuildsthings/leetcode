# https://leetcode.com/problems/network-delay-time/
# difficulty: medium
# tags: graphs, dijkstra

# Problem
# You are given a network of n nodes, labeled from 1 to n. You are also given times, a list of travel times as directed edges times[i] = (ui, vi, wi), where ui is the source node, vi is the target node, and wi is the time it takes for a signal to travel from source to target.

# We will send a signal from a given node k. Return the minimum time it takes for all the n nodes to receive the signal. If it is impossible for all the n nodes to receive the signal, return -1.

# Solution
# Standard djikstra

class Solution:
    def networkDelayTime(self, times: List[List[int]], n: int, k: int) -> int:
        edgeMap = defaultdict(dict)

        for a, b, w in times:
            edgeMap[a][b] = w

        heap = [[0, k]] # time to get there, node
        shortest = {node: float('inf') for node in range(1, n + 1)} # shortest time to get to a node
        res = 0

        while heap:
            time, node = heapq.heappop(heap)
            if time >= shortest[node]:
                continue
            shortest[node] = time
            for adj in edgeMap[node]:
                newTime = time + edgeMap[node][adj]
                # pruning
                if shortest[adj] <= newTime:
                    continue

                heapq.heappush(heap, [newTime, adj])

        res = max(shortest.values())
        return res if res != float('inf') else -1

