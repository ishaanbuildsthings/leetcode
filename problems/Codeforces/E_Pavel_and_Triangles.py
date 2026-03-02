n = int(input())
arr = list(map(int, input().split()))
res = 0
left = 0
for i in range(n):
    take = min(left, arr[i] // 2)
    res += take
    arr[i] -= 2 * take
    left -= take

    trips = arr[i] // 3
    res += trips
    arr[i] -= trips * 3

    left += arr[i]

print(res)

