
def solve():
    n, q = map(int, input().split())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    res = []
    for i in range(n - 1, -1, -1):
        if i == n - 1:
            A[i] = max(A[i], B[i])
        else:
            A[i] = max(A[i], B[i], A[i + 1])

    pf = []
    curr = 0
    for v in A:
        curr += v
        pf.append(curr)
    
    def query(l, r):
        if l == 0:
            return pf[r]
        return pf[r] - pf[l - 1]
    
    for _ in range(q):
        l, r = map(int, input().split())
        l -= 1
        r -= 1
        res.append(query(l, r))
    print(*res)


t = int(input())
for _ in range(t):
    solve()


