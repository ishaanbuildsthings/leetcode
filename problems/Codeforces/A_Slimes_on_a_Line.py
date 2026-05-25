def solve():
    n = int(input())
    A = list(map(int, input().split()))
    A.sort()
    median = (A[0] + A[-1]) // 2
    mxDist = max(median - A[0], A[-1] - median)
    print(mxDist)
t = int(input())
for _ in range(t):
    solve()