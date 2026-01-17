class Solution:
    def minimumFlips(self, n: int, edges: List[List[int]], start: str, target: str) -> List[int]:
        deg = [0] * n
        g = [[] for _ in range(n)] # g[node1] holds (node2, edgeIdx)
        for i, (a, b) in enumerate(edges):
            deg[a] += 1
            deg[b] += 1
            g[a].append((b, i))
            g[b].append((a, i))

        res = []
        q = deque([node for node in range(n) if deg[node] == 1])

        topo = []
        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                topo.append(popped)
                for adj, edgeI in g[popped]:
                    deg[adj] -= 1
                    if deg[adj] == 1:
                        q.append(adj)
        
        res = []
        state = list([int(x) for x in start])
        seenTopos = set()
        for node in topo:
            seenTopos.add(node)
            if state[node] == int(target[node]):
                continue
            for adj, edgeI in g[node]:
                if adj in seenTopos:
                    continue
                state[adj] ^= 1
                state[node] ^= 1
                res.append(edgeI)
        
        if all(state[i] == int(target[i]) for i in range(n)):
            return sorted(res)
        return [-1]

