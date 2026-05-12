# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# ⚠️  Notconstant-factor optimised
# ⚠️ Probably missing a lot of functionality

import heapq

# Takes in edges [fromNode, toNode, edgeWeight]
# Takes in a list of the nodes to make the matrix graph easy
# Node range must be dense

# O(max(nodes) space
class DijkstraWeightedDirectedDenseNodes:
    def __init__(self, edges, nodesList):
        self.maxNode = max(nodesList)

        # adjMap[fromNode][toNode] = minimum weight
        self.adjMap = [dict() for _ in range(self.maxNode + 1)]
        for fromNode, toNode, w in edges:
          if not toNode in self.adjMap[fromNode]:
            self.adjMap[fromNode][toNode] = w
          else:
            self.adjMap[fromNode][toNode] = min(self.adjMap[fromNode][toNode], w)


    def minDistsFromSource(self, source):
        """Returns a list `minDist` where minDist[target] is the shortest distance from `source` to `target`."""
        minDist = [inf] * (self.maxNode + 1)

        heap = [(0, source)] # holds (distance, node)

        while heap:
          distance, node = heapq.heappop(heap)
          if minDist[node] <= distance:
            continue
          minDist[node] = distance
          for adjNode, adjW in self.adjMap[node].items():
            newDist = distance + adjW
            if newDist < minDist[adjNode]:
              heapq.heappush(heap, (newDist, adjNode))

        return minDist


class Solution:
    def findMaxPathScore(self, edges: List[List[int]], online: List[bool], k: int) -> int:
        l = 0
        r = max([t[2] for t in edges], default=0)
        res = None
        n = len(online)
        
        def canTravelAbove(minAllowed):
            es = []
            for a, b, w in edges:
                if w < minAllowed:
                    continue
                if not online[a] or not online[b]:
                    continue
                es.append([a, b, w])
            dji = DijkstraWeightedDirectedDenseNodes(es, list(range(n)))
            dist = dji.minDistsFromSource(0)[n-1]
            return dist <= k

        while l <= r:
            m =(r+l)//2
            if canTravelAbove(m):
                res = m
                l = m + 1
            else:
                r = m - 1
        if res is None:
            return -1
        return res