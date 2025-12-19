import sys
def solve():
    data = sys.stdin.read().split()
    it   = iter(data)
    N    = int(next(it))
    W    = int(next(it))
    items = []
    for _ in range(N):
        w = int(next(it))
        v = int(next(it))
        items.append((w, v)) # list of (weights, values)
    
    dp = [[0] * (W+1) for _ in range(N + 1)]
    # dp[item][w] tells us the most we can get after considering `item` items and we stuff exactly w into our bag
    
    for item in range(1, N+1):
      itemWeight, itemValue = items[item-1]
      for bagWeight in range(W + 1):
        # we could take the best for 0...item-1 with stuffing exactly bagWeight-itemWeight into our bag
        # because then if we take this item we are now 0...item with exactly bagWeight
        if bagWeight - itemWeight >= 0:
          dp[item][bagWeight] = dp[item - 1][bagWeight - itemWeight] + itemValue
        # we could also not take this item, so we use the previous best
        dp[item][bagWeight] = max(dp[item][bagWeight], dp[item-1][bagWeight])
    
    print(max(dp[-1]))
        
        
        

if __name__ == "__main__":
    solve()