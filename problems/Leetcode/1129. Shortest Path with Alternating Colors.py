class Solution:
    def shortestAlternatingPaths(self, n: int, redEdges: List[List[int]], blueEdges: List[List[int]]) -> List[int]:
        redEdgeMap = defaultdict(list)
        blueEdgeMap = defaultdict(list)
        for a, b in redEdges:
            redEdgeMap[a].append(b)
        for a, b in blueEdges:
            blueEdgeMap[a].append(b)

        def bfs(nextEdgeColor, end):
            q = collections.deque()
            q.append(0)

            seenViaBlueEdge = set()
            seenViaRedEdge = set()
            if nextEdgeColor == 'red':
                seenViaBlueEdge.add(0)
            else:
                seenViaRedEdge.add(0)
                
            steps = 0

            if end == 0:
                return 0

            while q:
                steps += 1
                length = len(q)
                for _ in range(length):
                    node = q.popleft()
                    for adj in (redEdgeMap[node] if nextEdgeColor == 'red' else blueEdgeMap[node]):
                        if adj == x:
                            return steps
                        if adj in (seenViaRedEdge if nextEdgeColor == 'red' else seenViaBlueEdge):
                            continue
                        if nextEdgeColor == 'blue':
                            seenViaBlueEdge.add(adj)
                        else:
                            seenViaRedEdge.add(adj)
                        q.append(adj)
                nextEdgeColor = 'red' if nextEdgeColor == 'blue' else 'blue'

            return -1
        
        res = []
        for x in range(n):
            redStart = bfs('red', x)
            blueStart = bfs('blue', x)
            if redStart != -1 or blueStart != -1:
                res.append(min(redStart, blueStart) if min(redStart, blueStart) != -1 else redStart if redStart != -1 else blueStart)
            else:
                res.append(-1)
        return res



