n = int(input())
arr = list(map(int, input().split()))
res = 0
mx = arr[0]
for i in range(1, n):
    if arr[i] >= mx:
        mx = arr[i]
        continue
    res += mx - arr[i]
    arr[i] = mx
print(res)