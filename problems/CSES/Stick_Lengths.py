n = int(input())
A = sorted(map(int, input().split()))
median = A[n // 2]
res = 0
for v in A:
    res += abs(v - median)
print(res)