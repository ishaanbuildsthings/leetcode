import sys

def read_input() -> tuple[int, list[float]]:
    data = sys.stdin.read().strip().split()
    n = int(data[0])
    probs = list(map(float, data[1:]))
    return n, probs

if __name__ == "__main__":
    N, p = read_input()
    dp = [[0] * (N + 1) for _ in range(N)] # dp[i][currHeads] is the chance to get exactly that many heads in i...0
    dp[0][1] = p[0]
    dp[0][0] = 1 - p[0]
    for i in range(1, N):
      chanceHeads = p[i]
      chanceTails = 1 - chanceHeads
      for currHeads in range(i + 2):
        if currHeads:
          prevOneLessHead = dp[i-1][currHeads - 1]
          getHead = prevOneLessHead * chanceHeads
        else:
          getHead = 0
        prevSameHead = dp[i-1][currHeads]
        getTail = prevSameHead * chanceTails
        dp[i][currHeads] = getHead + getTail
    
    res = 0
    for headAmount in range(len(dp[-1])):
      if headAmount > N / 2:
        res += dp[-1][headAmount]
    
    print(res)
      
      