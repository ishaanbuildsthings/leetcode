#     1
#   2  3
#  5    4

# every even depth (0-index) we can pick the color type for that row
T = int(input())
for _ in range(T):
    N, Q = map(int, input().split())

    g = [[] for _ in range(N)]
    for _ in range(N - 1):
        a, b = map(int, input().split())
        g[a-1].append(b-1)
        g[b-1].append(a-1)
    
    depths = [0] * N
    
    childrenSizes = [0] * N # number of children each node as
    
    stack = [(0, -1, 0)]
    while stack:
        node, parent, level = stack.pop()
        depths[node] = level
        for adj in g[node]:
            if adj == parent:
                continue
            childrenSizes[node] += 1
            stack.append((adj, node, level + 1))
    
    components = []
    for node in range(N):
        if depths[node] % 2 == 0:
            children = childrenSizes[node]
            components.append(abs(children - 1))
    
    tot = sum(components)
    if Q == 1:
        print(tot)
        continue
    
    # otherwise, we need to partition these pieces into two groups, check for the doable group 1 sizes
    # find the closest size to half the sum
    
    bs = 1 # doable group 1 sizes
    # I think this is S * root n / W but not sure how to prove it, I see that it happens with rootN unique components of size 1 + 2 + 3 + ... + root N.
    for c in components:
        bs |= bs << c
    
    half = tot // 2
    
    # this can be optimized I think since we can check if a bit is set in O(1) with a proper bitset, otherwise this is n^2 / W which is fast enough anyway
    res = float('inf')
    for offset in range(N + 1):
        if bs & (1 << offset):
            res = min(res, 2 * abs(half - offset))
    print(res)