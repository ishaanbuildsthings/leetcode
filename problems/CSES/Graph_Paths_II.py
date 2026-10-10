inf = 2 * 10**18

min = lambda x, y : x if x < y else y

n, m, k = map(int, input().split())
adj = [[inf for _ in range(n)] for _ in range(n)] # adj[node1][node2] = min direct edge
for _ in range(m):
    a, b, w = map(int, input().split())
    a -= 1
    b -= 1
    adj[a][b] = min(adj[a][b], w)

def compose(m1, m2):
    m3 = [[inf for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for c in range(n):
            for b in range(n):
                c1 = m1[a][b]
                c2 = m2[b][c]
                m3[a][c] = min(m3[a][c], c1 + c2)
    return m3

def matPow(transitions):
    if transitions == 1:
        return adj
    if transitions % 2:
        return compose(adj, matPow(transitions - 1))
    half = matPow(transitions // 2)
    return compose(half, half)

powed = matPow(k)
answer = powed[0][n - 1]
print(answer if answer < inf else -1)
    