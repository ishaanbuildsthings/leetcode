import sys
input = sys.stdin.readline

N, K = map(int, input().split())
h = list(map(int, input().split()))

dp = [0] * (N + 1) # dp[stone] tells us the min cost to reach that stone, 1 indexed
dp[1] = 0
for stone in range(2, len(dp)):
  resHere = 1000000000
  for prev in range(1, K + 1):
    newPos = stone - prev
    if newPos <= 0:
      break
    resHere = min(resHere, abs(h[stone-1] - h[newPos-1]) + dp[newPos])
  dp[stone] = resHere

print(dp[N])
    