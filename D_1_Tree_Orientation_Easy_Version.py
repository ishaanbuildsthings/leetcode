def solve():
    # print('----------')
    n = int(input())
    grid = []
    for _ in range(n):
        row = str(input())
        row = [int(x) for x in row]
        grid.append(row)

    # just first make sure every node can reach itself
    for i in range(n):
        if not grid[i][i]:
            # print(f'node couldnt even reach itself!!!') # TODO REMOVE THIS ----------------------------------------
            print('No')
            return

    sinks = []
    for i in range(n):
        row = grid[i]
        # print(f'{row=} sum is: {sum(row)}')
        if (sum(row) == 1) and row[i] == 1:
            sinks.append(i)

    # print(f'init sinks: {sinks}')

    edges = []
    wasSink = set()

    while len(wasSink) + len(sinks) < n:
        nsinks = [] # new layer of sinks we will generate
        connected = set() # which ones got claimed

        sinkSet = set(sinks)
        for node in range(n):
            # we are considering potential new sinks
            # skip any node that was already a sink or is a current sink
            if node in wasSink or node in sinkSet:
                continue

            reach = grid[node]
            failFound = False
            for target in range(len(reach)):
                didHit = reach[target] == 1
                if didHit:
                    if target in sinkSet:
                        continue
                    if target in wasSink:
                        continue
                    if target == node:
                        continue
                    failFound = True

            if failFound:
                continue

            reachable = [j for j in range(n) if j != node and reach[j] == 1]
            for target in reachable:
                if target in sinkSet:
                    if all(grid[t][target] == 0 for t in reachable if t != target):
                        edges.append([node, target])
                        connected.add(target)
            nsinks.append(node)

        if not nsinks:
            print('No')
            return

        for s in sinks:
            # if we got claimed, its no longer a valid sink, demote to was sink
            if s in connected:
                wasSink.add(s)
            else:
                # if we were not claimed its part of the new layers
                nsinks.append(s)
        sinks = nsinks

    # ensure right # of edges
    if len(edges) != n - 1:
        print('No')
        return

    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    stack = [0]
    seen[0] = True
    count = 0
    # dfs to check its 1 component
    while stack:
        node = stack.pop()
        count += 1
        for adjN in adj[node]:
            if not seen[adjN]:
                seen[adjN] = True
                stack.append(adjN)
    if count != n:
        print('No')
        return

    # actually validate
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
    for source in range(n):
        reach = [0] * n
        reach[source] = 1
        stack = [source]
        while stack:
            node = stack.pop()
            for adjN in adj[node]:
                if not reach[adjN]:
                    reach[adjN] = 1
                    stack.append(adjN)
        if reach != grid[source]:
            print('No')
            return

    print('Yes')
    for a, b in edges:
        print(f'{a+1} {b+1}')

t = int(input())
for _ in range(t):
    solve()