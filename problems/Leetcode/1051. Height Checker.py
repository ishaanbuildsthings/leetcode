class Solution:
    def heightChecker(self, heights: List[int]) -> int:
        # can do bucket sort also
        return sum(
        sorted(heights)[i] != heights[i] for i in range(len(heights)))