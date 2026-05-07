n = int(input())
arr = list(map(int, input().split()))
 
dp = [arr[0]] # dp[x] is the lowest ending number of a subsequence of length x+1
 
for num in arr[1:]:
  # binary search for the furthest right index with a number < num
  l = 0
  r = len(dp) - 1
  resRight = None
  while l <= r:
    m = (r + l) // 2
    if dp[m] < num:
      resRight = m
      l = m + 1
    else:
      r = m - 1
  if resRight is None:
    dp[0] = num
  else:
    if resRight == len(dp) - 1:
      dp.append(num)
    else:
      dp[resRight + 1] = num
 
print(len(dp))