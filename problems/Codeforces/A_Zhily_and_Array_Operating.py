def solve():
    n = int(input())
    A = list(map(int, input().split()))
    for i in range(n - 2, -1, -1):
        if A[i + 1] > 0:
            A[i] += A[i + 1]
    print(sum(1 if x > 0 else 0 for x in A))
t = int(input())
for _ in range(t):
    solve()