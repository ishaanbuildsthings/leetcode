class Solution:
    def fillCups(self, amount: List[int]) -> int:
        mx1 = max(amount)
        mx2 = ceil(sum(amount) / 2)
        return max(mx1, mx2)