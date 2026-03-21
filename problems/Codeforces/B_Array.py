t = int(input())
for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    res = [None] * n
    INF = 10**18
    NINF = -1 * INF
    for i in range(n):
        v = A[i]
        withInf = 0
        withNinf = 0
        for j in range(i + 1, n):
            if abs(A[i] - INF) > abs(A[j] - INF):
                withInf += 1
            if abs(A[i] - NINF) > abs(A[j] - NINF):
                withNinf += 1
        res[i] = max(withInf, withNinf)

    print(*res)
