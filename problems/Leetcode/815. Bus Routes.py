class Solution:
    def numBusesToDestination(self, routes: List[List[int]], source: int, target: int) -> int:
        stopToBus = defaultdict(list) # maps a stop -> list of buses with that stop

        for bus in range(len(routes)):
            for stop in routes[bus]:
                stopToBus[stop].append(bus)
        
        edgeSet = set() # (bus1, bus2) means they share a stop and would cost 1 to go between
        for stop, bucket in stopToBus.items():
            for i in range(len(bucket)):
                bus1 = bucket[i]
                for j in range(i + 1, len(bucket)):
                    bus2 = bucket[j]
                    edgeSet.add((bus1, bus2))
                    edgeSet.add((bus2, bus1))
        
        edges = list(edgeSet)
        adj = defaultdict(list)
        for a, b in edges:
            adj[a].append(b)

        startBuses = []
        endBuses = set()
        for bus in range(len(routes)):
            if source in routes[bus]:
                startBuses.append(bus)
            if target in routes[bus]:
                endBuses.add(bus)
                
        if source == target:
            return 0
        
        steps = 0
        q = deque(startBuses)
        seen = set(startBuses)
        while q:
            length = len(q)
            for _ in range(length):
                bus = q.popleft()
                if bus in endBuses:
                    return steps + 1
                for adjB in adj[bus]:
                    if adjB in seen:
                        continue
                    seen.add(adjB)
                    q.append(adjB)
            steps += 1
        
        return -1
                



