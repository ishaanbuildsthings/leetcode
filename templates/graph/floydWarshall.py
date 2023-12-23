# variables
# replace ITERABLE_EDGES with an array of [from, to, weight]
# set n to be the number of nodes, numbered from 0 to n-1

# access
# we can access the distance between two nodes with dist[i][j]

# n^3 time and space

edgeMap = defaultdict(lambda: defaultdict(lambda: float('inf')))
for a, b, w in ITERTABLE_EDGES:
    edgeMap[a][b] = w
    edgeMap[b][a] = w

dist = [[float('inf')] * n for _ in range(n)] # dist from i to j
for i in range(n):
    for j in range(n):
        if i == j:
            dist[i][j] = 0
            continue
        dist[i][j] = edgeMap[i][j] # add edges if they exist

for k in range(n):
    for i in range(n):
        for j in range(n):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])