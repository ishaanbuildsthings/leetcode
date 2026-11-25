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
                dist = minDist(node, target, n)
                if dist <= distanceThreshold:
                    reach[node] += 1
        mn = min(reach)
        for i in range(n - 1, -1, -1):
            if reach[i] == mn:
                return i
