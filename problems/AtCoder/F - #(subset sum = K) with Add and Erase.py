Q, K = map(int, input().split())
MOD = 998244353
dp = [0] * (K + 1) # dp[x] is the number of ways to make x
dp[0] = 1

for _ in range(Q):
    query = input().split()
    op = query[0]
    x = int(query[1])
    
    if op == '+':
      for make in range(K, -1, -1):
        prev = make - x
        if prev < 0:
          continue
        prevWays = dp[prev]
        dp[make] += prevWays
        dp[make] %= MOD
    else:
      for make in range(K + 1):
        prev = make - x
        if prev < 0:
          continue
        prevWays = dp[prev]
        dp[make] -= prevWays
        dp[make] %= MOD
    
    print(dp[K])