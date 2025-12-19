def parseInput():
    import sys
    data = sys.stdin.read().split()
    
    n = int(data[0])
    sequence = list(map(int, data[1:1+n]))
    
    return n, sequence

n, sequence = parseInput()

dp = [[-1] * n for _ in range(n)]
for i in range(n):
  dp[i][i] = sequence[i] # player 1 can take that element

for length in range(2, n + 1):
  for l in range(n):
    r = l + length - 1
    if r >= n:
      break
    takeLeft = sequence[l] - dp[l + 1][r]
    takeRight = sequence[r] - dp[l][r - 1]
    dp[l][r] = max(takeLeft, takeRight)

print(dp[0][-1])