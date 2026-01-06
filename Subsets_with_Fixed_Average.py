n, avg = map(int, input().split())
arr = list(map(int, input().split()))
tot = sum(arr)
dp = [
    [
        0 for _ in range(n + 1)
    ] for _ in range(tot + 1)
]
dp[0][0] = 1
# dp[sum][size] = the number of ways to form that subset
pfSum = 0
for i, v in enumerate(arr):
    for prevSum in range(pfSum, -1, -1):
        for prevSize in range(i, -1, -1):
            dp[prevSum + v][prevSize + 1] += dp[prevSum][prevSize]
    
    pfSum += v

# print(dp)
res = 0
for total in range(tot + 1):
    for sz in range(1, n + 1):
        if total / sz != avg:
            continue
        res += dp[total][sz]
print(res)
