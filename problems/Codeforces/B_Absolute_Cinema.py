def solve():
    n = int(input())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    res = 0
    for i in range(n):
        if B[i] < A[i]:
            B[i], A[i] = A[i], B[i]
    print(sum(B) + max(A))

t = int(input())
for _ in range(t):
    solve()