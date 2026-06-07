class Solution:
    def maxContainers(self, n: int, w: int, maxWeight: int) -> int:
        return min(n**2, maxWeight // w)