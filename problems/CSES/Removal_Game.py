n = int(input())
arr = list(map(int, input().split()))
 
dp = [[0] * n for _ in range(n)] # dp[l][r] is the best for player one in l...r
 
p1OnSingle = (n % 2 == 1)
for pos in range(n):
    dp[pos][pos] = arr[pos] if p1OnSingle else 0
 
for subarrayLength in range(2, n + 1):
  for leftIndex in range(n):
    movesMade = n - subarrayLength
    isP1 = (movesMade % 2) == 0
    r = leftIndex + subarrayLength - 1
    if r >= len(arr):
      break
    ifPlayerTakesLeft = dp[leftIndex + 1][r] + (arr[leftIndex] if isP1 else 0)
    ifPlayerTakesRight = dp[leftIndex][r-1] + (arr[r] if isP1 else 0)
    if isP1:
      res = max(ifPlayerTakesLeft, ifPlayerTakesRight)
    else:
      res = min(ifPlayerTakesLeft, ifPlayerTakesRight)
    dp[leftIndex][r] = res
print(dp[0][n - 1])
