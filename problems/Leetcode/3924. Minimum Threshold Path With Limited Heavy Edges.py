class Solution:
    def minimumThreshold(self, n: int, edges: List[List[int]], source: int, target: int, k: int) -> int:
        # binary search on answer
        # for each iteration we run a 01 bfs

        # wt means everything <= wt is light
        def check(wt):
            adj = defaultdict(list)
            for a, b, w in edges:
                if w <= wt:
                    adj[a].append((b, 0))
                    adj[b].append((a, 0))
                else:
                    adj[a].append((b,1))
                    adj[b].append((a,1))

            q = deque()
            q.append((source, 0)) # holds (node, cost)

            minDists = [inf] * n

            while q:
                node, cost = q.popleft()
                if cost >= minDists[node]:
                    continue
                minDists[node] = cost
                for adjN, adjW in adj[node]:
                    nwt = adjW + cost
                    if nwt >= minDists[adjN]: continue
                    if adjW == 0:
                        q.appendleft((adjN, nwt))
                    else:
                        q.append((adjN, nwt))

            ans = minDists[target]
            return ans <= k
                    
            

        l = 0
        r = 10**9 + 10
        resW = None
        while l <= r:
            m = (l + r) // 2
            if check(m):
                resW = m
                r = m - 1
            else:
                l = m + 1

        if resW is None:
            return -1

        return resW
            