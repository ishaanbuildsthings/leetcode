class Solution:
    def findKthSmallest(self, coins: List[int], k: int) -> int:
        def waysLTEAmount(amount):
            totalWays = 0
            for mask in range(1, 1 << len(coins)):
                selected = mask.bit_count()
                nums = []
                for i in range(len(coins)):
                    if mask >> i & 1:
                        nums.append(coins[-(i+1)])
                value = math.lcm(*nums)
                if selected % 2:
                    totalWays += amount // value
                else:
                    totalWays -= amount // value
            return totalWays
        
        l = 0
        r = min(coins) * k
        res = None
        while l<=r:
            m = (r + l) // 2
            ways = waysLTEAmount(m)
            if ways < k:
                l = m + 1
            elif ways == k:
                res = m
                r = m - 1
            else:
                r = m - 1
        return res