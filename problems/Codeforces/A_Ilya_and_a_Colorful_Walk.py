n = int(input())
arr = list(map(int, input().split()))
res = -10**9
leftDiff = None
for i in range(n - 1, -1, -1):
    if arr[i] != arr[0]:
        res = i
        break
for i in range(n):
    if arr[i] != arr[-1]:
        res = max(res, n - i - 1)
        break
print(res)
        
