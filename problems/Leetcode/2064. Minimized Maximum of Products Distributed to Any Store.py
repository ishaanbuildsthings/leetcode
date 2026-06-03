class Solution:
    def minimizedMaximum(self, n: int, quantities: List[int]) -> int:

        def isPossible(m):
            return sum(math.ceil(amount / m) for amount in quantities) <= n

        l = 1
        r = max(quantities)
        while l <= r:
            m = (r + l) // 2
            if isPossible(m):
                r = m - 1
            else:
                l = m + 1
        
        return l


