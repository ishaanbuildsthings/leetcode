# djikstra to get shortest distance from source to all nodes
# given n nodes numbered 0 to n-1
# requires edgeMap[fromNode][toNode] = weight
# requires n = # of nodes
import heapq
def djikstra(source):
    heap = [[0, source]] # time to get there, node
    shortest = {node: float('inf') for node in range(1, n + 1)} # shortest time to get to a node

    while heap:
        time, node = heapq.heappop(heap)
        # if we pop and aren't shortest, necessary skip
        if time >= shortest[node]:
            continue
        shortest[node] = time
        for adj in edgeMap[node]:
            newTime = time + edgeMap[node][adj]
            # pruning
            if shortest[adj] <= newTime:
                continue

            heapq.heappush(heap, [newTime, adj])
    return shortest


# djikstra to get shortest distance to one node
def djikstra(source, target):
    heap = [[0, source]] # time to get there, node
    shortest = {node: float('inf') for node in range(1, n + 1)} # shortest time to get to a node

    while heap:
        time, node = heapq.heappop(heap)
        if node == target:
            return time

        # if we pop and aren't shortest, necessary skip
        if time >= shortest[node]:
            continue
        shortest[node] = time
        for adj in edgeMap[node]:
            newTime = time + edgeMap[node][adj]
            # pruning
            if shortest[adj] <= newTime:
                continue

            heapq.heappush(heap, [newTime, adj])

    return float('inf')