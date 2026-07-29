class Solution:
    def minCostToMoveChips(self, position: List[int]) -> int:
        oddCounts = sum(
            position[i]% 2 == 1 for i in range(len(position))
        )
        evenCounts = len(position) - oddCounts
        return min(oddCounts, evenCounts)