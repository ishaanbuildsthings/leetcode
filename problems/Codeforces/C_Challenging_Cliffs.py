from collections import Counter
t = int(input())

for _ in range(t):
    n = int(input())
    A = list(map(int, input().split()))
    A.sort()
    if len(A) == 2:
        print(*A)
        continue
    minDiff = min(abs(A[i] - A[i + 1]) for i in range(n - 1))
    
    for i in range(n - 1):
        if A[i + 1] - A[i] == minDiff:
            # start is i+1..., end is ...i
            start = i + 1
            break
    
    res = []
    for i in range(start, n):
        res.append(A[i])
    for i in range(start):
        res.append(A[i])
    drops = 0
    for i in range(n - 1):
        drops += res[i + 1] < res[i]
    print(*res)