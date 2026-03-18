class Solution:
    def minimalKSum(self, nums: List[int], k: int) -> int:
        def fn(n):
            return (n * (n + 1)) // 2
        def tot(low, high):
            # sum from 1 + 2 + ... + n
            ups = fn(high)
            lows = fn(low - 1)
            return ups - lows
            
        s = sorted(nums)
        used = 0
        ans = 0
        for i, num in enumerate(s):
            if used == k:
                break
            if num == 1:
                continue
            if not i:
                prev = 0
            else:
                prev = s[i - 1]
            if prev == num:
                continue
            if prev + 1 == num:
                continue
            prevUp = prev + 1
            down = num - 1
            width = down - prevUp + 1
            
            remain = k - used
            if remain > width:
                used += width
                ans += tot(prevUp, down)
                continue
            used = k
            actualUp = prevUp + remain - 1
            ans += tot(prevUp, actualUp)
        
        if used < k:
            remain = k - used
            high = s[-1]
            lowB = high + 1
            upB = lowB + remain - 1
            ans += tot(lowB, upB)
        
        return ans


