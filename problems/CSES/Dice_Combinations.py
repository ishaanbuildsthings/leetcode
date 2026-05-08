import sys
n = int(input())
MOD = 10**9 + 7
dp = [0] * (n + 1)
dp[0] = 1
for amount in range(1, n + 1):
  resHere = 0
  for prev in range(amount - 6, amount):
    if prev < 0:
      continue
    resHere += dp[prev]
  dp[amount] = resHere % MOD
 
print(dp[-1])
