def parseInput():
    import sys
    input = sys.stdin.read
    data = input().split()
    
    n = int(data[0])
    w = int(data[1])
    
    weights = []
    values = []
    
    index = 2
    for _ in range(n):
        weight = int(data[index])
        value = int(data[index + 1])
        weights.append(weight)
        values.append(value)
        index += 2
    
    return n, w, weights, values

n, maxCapacity, weights, values = parseInput()
MAX_VALUE = sum(values)
INF = 10**18
dp = [INF] * (MAX_VALUE + 1) # dp[value] is the minimum weight we can get to form that value

dp[0] = 0

for i in range(n):
  w = weights[i]
  v = values[i]
  for prevMadeValue in range(MAX_VALUE, -1, -1):
    if dp[prevMadeValue] == INF:
      continue
    pushed = v + prevMadeValue
    if pushed >= len(dp):
      continue
    dp[pushed] = min(dp[pushed], w + dp[prevMadeValue])

res = 0
for i in range(len(dp) - 1, -1, -1):
  if dp[i] <= maxCapacity:
    res = i
    break
print(res)
    
    


