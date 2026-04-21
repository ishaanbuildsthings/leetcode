class Solution:
    def minCost(self, m: int, n: int) -> int:
        if min(m, n) > 1:
            return -1
        if max(n, m) > 2:
            return -1
        if n == m == 1:
            return 1
        return 3