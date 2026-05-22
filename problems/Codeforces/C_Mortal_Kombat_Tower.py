numTests = int(input())
testCases = []
for _ in range(numTests):
    n = int(input())
    bossTypes = list(map(int, input().split()))
    testCases.append(bossTypes)

# print(f"testCases={testCases}")

def solve(bosses):
  # print(f'solving: {bosses}')
  INF = 10**18
  dp = [[INF] * 2 for _ in range(len(bosses) + 1)] # dp[howManyHaveBeenKilled][whoJustWent] is the answer for that up to ...i
  dp[0][0] = 0 # our friends turn to start

  for i in range(len(bosses)):
     # if were going now
     resHere = dp[i+1][0]
     if i > 0:
      ifKill1 = dp[i][1]
      resHere = min(resHere, ifKill1)
     if i > 1:
        ifKill2 = dp[i-1][1]
        resHere = min(resHere, ifKill2)
     dp[i+1][0] = resHere

     # if our friend is going
     resHere = dp[i+1][1]
     ifKill1 = dp[i][0] + bosses[i]
     resHere = min(resHere, ifKill1)
     if i > 0:
        ifKill2 = dp[i-1][0] + bosses[i] + bosses[i-1]
        resHere = min(resHere, ifKill2)
     dp[i+1][1] = resHere

  res = (min(dp[-1][0], dp[-1][1]))
  # print(f'res={res}')
  return res

# print(solve(testCases[0]))
for t in testCases:
   print(solve(t))



 