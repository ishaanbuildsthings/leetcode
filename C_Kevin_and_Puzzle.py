from collections import deque

input = sys.stdin.readline
MOD = 998244353

def solve():
    n = int(input())
    a = list(map(int, input().split()))
    
    honestIdx, honestVal = 0, 1
    L = deque([0])
    
    for i in range(n):
        hVal = 0
        if a[i] == honestIdx:
            hVal = (hVal + honestVal) % MOD
        if a[i] < len(L):
            hVal = (hVal + L[a[i]]) % MOD
        
        L.clear()
        for _ in range(honestIdx + 2):
            L.append(0)
        L[honestIdx + 1] = honestVal
        
        honestIdx, honestVal = a[i], hVal
    
    total = (honestVal + sum(L)) % MOD
    print(total)

t = int(input())
for _ in range(t):
    solve()