class Solution:
    def crackSafe(self, n: int, k: int) -> str:
        if n == 1:
            res = [str(d) for d in range(k)]
            return ''.join(res)
        
        smallN = n - 1
        nodes = []
        def bt(s):
            if len(s) == smallN:
                nodes.append(s)
                return
            for d in range(k):
                bt(s + str(d))
        bt('')

        g = defaultdict(list)
        for node in nodes:
            for d in range(k):
                nnode = node + str(d)
                nnode = nnode[1:]
                g[node].append(nnode)
        
        path = deque()
        def dfs(node):
            while g[node]:
                nxt = g[node].pop()
                dfs(nxt)
            path.appendleft(node)
        
        dfs(nodes[0])

        path = list(path)
        return path[0] + ''.join(node[-1] for node in path[1:])