class Solution:
    def maxDistance(self, s: str, k: int) -> int:
        res = 0
        c = Counter()
        for move in s:
            c[move] += 1
            
            # try to go right and up
            r = c['E']
            l = c['W']
            u = c['N']
            d = c['S']
            
            swapLtoR = min(k, l)
            remainSwap = k - swapLtoR
            swapDToU = min(remainSwap, d)
            
            newRightDelta = (r + swapLtoR) - (l - swapLtoR)
            newUpDelta = (u + swapDToU) - (d - swapDToU)
            res = max(res, abs(newRightDelta) + abs(newUpDelta))
            
            # go right and down
            swapUToD = min(remainSwap, u)
            newDownDelta = (d + swapUToD) - (u - swapUToD)
            res = max(res, abs(newRightDelta) + abs(newDownDelta))
            
            # go left and up
            swapRToL = min(k, r)
            remainSwap = k - swapRToL
            newLeftDelta = (l + swapRToL) - (r - swapRToL)
            
            swapDToU = min(remainSwap, d)
            newUpDelta = (u + swapDToU) - (d - swapDToU)
            res = max(res, abs(newLeftDelta) + abs(newUpDelta))
            
            # go left and down
            swapUToD = min(remainSwap, u)
            newDownDelta = (d + swapUToD) - (u - swapUToD)
            res = max(res, abs(newLeftDelta) + abs(newDownDelta))
        
        return res
            
            