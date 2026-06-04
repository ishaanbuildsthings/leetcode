class Solution:
    def maxProfit(self, inventory: List[int], orders: int) -> int:

        def oneToN(n):
            return n * (n + 1) // 2
        
        # sum of l + (l+1) + ... + r
        def tot(l, r):
            up = oneToN(r)
            down = 0 if l <= 1 else oneToN(l - 1)
            return up - down

        inventory.sort(reverse=True)
        res = 0
        MOD = 10**9 + 7
        width = 1
        i = 0
        while orders:
            nxt = inventory[i + 1] if i < len(inventory) - 1 else 0
            height = inventory[i]
            diff = height - nxt
            canMakeOrders = width * diff
            if canMakeOrders <= orders:
                orders -= canMakeOrders
                singleBar = tot(nxt + 1, height)
                res += singleBar * width
                width += 1
                i += 1
                continue
            
            fullWidthsUsed = orders // width
            R = height
            L = R - fullWidthsUsed + 1
            singleBar = tot(L, R)
            res += singleBar * width
            partials = orders - (fullWidthsUsed * width)
            partialSize = L - 1
            res += partials * partialSize
            break
        
        return res % MOD
            


