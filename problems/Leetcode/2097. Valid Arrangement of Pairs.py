class Solution:
    def validArrangement(self, pairs):
        
        g = defaultdict(list)
        inDeg = defaultdict(int)
        outDeg = defaultdict(int)
        for a, b in pairs:
            g[a].append(b)
            inDeg[b] += 1
            outDeg[a] += 1
        
        start = pairs[0][0]
        for node in g:
            if outDeg[node] == inDeg[node] + 1:
                start = node
        
        path = deque()

        def dfs(node):
            while g[node]:
                nxt = g[node].pop()
                dfs(nxt)
            path.appendleft(node)
        dfs(start)
        
        res = []
        for i in range(len(path) - 1):
            node = path[i]
            nxt = path[i+1]
            res.append([node, nxt])
        
        return res


        
        