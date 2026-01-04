n = int(input())
arr = list(map(int, input().split()))
eTot = n * (n + 1) // 2
print(eTot - sum(arr))