numCoins = int(input())
coinVals = list(map(int, input().split()))
 
dp = [0] * numCoins # using the coins from 0...i tells us a bitset of all the X values we can make
dp[0] = (1 << coinVals[0])
for i in range(1, len(coinVals)):
  prevMask = dp[i - 1]
  newMask = prevMask << coinVals[i]
  finalMask = prevMask | newMask | (1 << coinVals[i]) # just take this coin
  dp[i] = finalMask
 
lastMask = dp[-1]
print(bin(lastMask).count('1'))
for potentialMoneySum in range(1, (max(coinVals) * numCoins) + 1):
  if (lastMask >> potentialMoneySum) & 1:
    print(potentialMoneySum)
