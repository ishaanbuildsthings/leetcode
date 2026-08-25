class Solution:
    def minimumAddedCoins(self, coins: List[int], target: int) -> int:
#         counts = collections.Counter(coins)
        
#         maxPow2 = 1
#         while maxPow2 <= target:
#             maxPow2 *= 2
        
#         maxPow2 /= 2
#         maxPow2 = int(maxPow2)
        
        coins.sort()
        acc = 0
        res = 0
        
        for coin in coins:
            while acc < target and acc < coin - 1:
                acc = 2*acc + 1
                res += 1
            acc += coin if acc < target else 0
            
        while acc < target:
            acc = 2*acc + 1
            res += 1
        
        return res
        