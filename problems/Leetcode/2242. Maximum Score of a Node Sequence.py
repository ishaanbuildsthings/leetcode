class Solution:
    def maximumScore(self, scores: list[int], edges: list[list[int]]) -> int:
        adj = defaultdict(list) # maps node -> [(w, adjN), ...]
        for a, b in edges:
            adj[a].append((scores[b], b))
            adj[b].append((scores[a], a))
        n = len(scores)
        for node in range(n):
            adj[node].sort(reverse=True)

        res = -inf

        def process(a, b):
            tot = scores[a] + scores[b]

            # pick best A neighbor (that is not B) then best B neighbor that fits
            bestANeighbor = 0
            bestAScore = 0
            bucket = adj[a]
            if bucket[0][1] != b:
                bestANeighbor = bucket[0][1]
                bestAScore = bucket[0][0]
            else:
                bestANeighbor = bucket[1][1]
                bestAScore = bucket[1][0]
            
            bestBNeighbor = -1
            bestBScore = 0
            bucket = adj[b]
            for w, adjN in bucket:
                if adjN == a or adjN == bestANeighbor:
                    continue
                bestBScore = w
                bestBNeighbor = adjN
                break
                
            if bestBNeighbor == -1:
                return -inf
            
            score1 = tot + bestAScore + bestBScore
            return score1

            

        for a, b in edges:
            if len(adj[a]) < 2 or len(adj[b]) < 2:
                continue
            score = max(process(a, b), process(b, a))
            res = max(res, score)
        
        return res if res != -inf else -1


                

