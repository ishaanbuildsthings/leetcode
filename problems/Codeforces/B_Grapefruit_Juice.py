t = int(input())
def solve():
    n, k, p = map(int, input().split())
    A = list(map(int, input().split()))
    A.sort()
    res = sum(A)

    pf = []
    curr = 0
    for v in A:
        curr += v
        pf.append(curr)
    
    def query(l, r):
        return pf[r] - (pf[l - 1] if l else 0)
    
    maxK = n // k

    for glasses in range(1, maxK + 1):
        joy = p * glasses
        eaten = glasses * k
        notEaten = n - eaten
        remain = query(n - 1 - notEaten + 1, n - 1)
        tot = remain + joy
        res = max(res, tot)
    
    print(res)
for _ in range(t):
    solve()