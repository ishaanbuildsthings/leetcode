n = int(input())
h = list(map(int, input().split()))

dp = [-1] * n # the cost to reach stone N (but we 0 index)
dp[0] = 0
for i in range(1, len(dp)):
  prevCost = dp[i - 1]
  prevCost += abs(h[i] - h[i - 1])
  resHere = prevCost
  if i > 1:
    prevPrevCost = dp[i-2]
    prevPrevCost += abs(h[i] - h[i - 2])
    resHere = min(resHere, prevPrevCost)
  dp[i] = resHere

print(dp[-1])