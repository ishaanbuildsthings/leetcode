n = int(input())
 
dp = [-1] * (n + 1) # the answer for X
dp[0] = 0
for num in range(1, n + 1):
  resHere = 100000000
  for digit in str(num):
    digitNum = int(digit)
    if digitNum == 0:
      continue
    newNum = num - digitNum
    resHere = min(resHere, 1 + dp[newNum])
  dp[num] = resHere
print(dp[num])