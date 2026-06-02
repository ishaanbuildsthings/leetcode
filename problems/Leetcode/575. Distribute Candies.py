class Solution:
    def distributeCandies(self, candyType: List[int]) -> int:
        unique = len(set(candyType))
        return min(unique, len(candyType) // 2)