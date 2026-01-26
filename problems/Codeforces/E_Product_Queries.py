import math
fmin = lambda x, y: x if x < y else y
def solve():
    n = int(input())
    A = list(map(int, input().split()))

    # dp[x] is min # of factors to form x
    dp = [float('inf')] * (n + 1)
    for v in A:
        dp[v] = 1
        

    def factorize(x):
        res = []
        mx = int(math.isqrt(x))
        for factor in range(1, mx + 1):
            if x % factor != 0:
                continue
            res.append(factor)
            other = x // factor
            if other != factor:
                res.append(other)
        return res
    
    for v in range(1, n + 1):
        factors = factorize(v)
        bestHere = float('inf')
        for fac in factors:
            other = v // fac
            bestHere = fmin(dp[other] + dp[fac], bestHere)
        dp[v] = fmin(dp[v], bestHere)
    
    res = []
    for fac in range(1, n + 1):
        v = dp[fac]
        if v == float('inf'):
            res.append(-1)
        else:
            res.append(v)
    
    print(*res)
                

t = int(input())
for _ in range(t):
    solve()