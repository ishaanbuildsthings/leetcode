n, x = map(int, input().split())
A = list((map(int, input().split())))
A = [(v, i) for i, v in enumerate(A)]
A.sort()
for i in range(len(A) - 2):
    j = i + 1
    k = n - 1
    while j < k:
        if A[i][0] + A[j][0] + A[k][0] == x:
            print(*[A[i][1] + 1, A[j][1] + 1, A[k][1] + 1])
            exit()
        elif A[i][0] + A[j][0] + A[k][0] > x:
            k -= 1
        else:
            j += 1
print("IMPOSSIBLE")
