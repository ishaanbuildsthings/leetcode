class Solution:
    def countServers(self, n: int, logs: List[List[int]], x: int, queries: List[int]) -> List[int]:
        logs.sort(key=lambda x: x[1])
        originalQueries = queries[:]
        queries.sort()

        queryAnswers = {}

        c = Counter() # which servers are currently in the query range
        l = 0
        r = -1
        for q in queries:
            ql = q - x
            qr = q
            while r + 1 < len(logs) and logs[r + 1][1] <= qr:
                r += 1
                gain = logs[r]
                server, time = gain
                c[server] += 1
            while l <= r and logs[l][1] < ql:
                lost = logs[l]
                server, time = lost
                c[server] -= 1
                if not c[server]: del c[server]
                l += 1
            uniq = len(c)
            queryAnswers[q] = n - uniq
        
        return [queryAnswers[q] for q in originalQueries]

