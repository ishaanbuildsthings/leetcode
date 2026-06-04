class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        lookingToBuy = 0
        holdingStock = -inf
        onCooldown = 0

        for i in range(len(prices)):
            newLookingToBuy = max(lookingToBuy, onCooldown)
            newHoldingStock = max(holdingStock, lookingToBuy - prices[i])
            newOnCooldown = holdingStock + prices[i]
            lookingToBuy = newLookingToBuy
            holdingStock = newHoldingStock
            onCooldown = newOnCooldown
        
        return max(lookingToBuy, onCooldown)






# looking to buy a stock     -\
# holding a stock            -\
# on cooldown                 - // goes to looking to buy