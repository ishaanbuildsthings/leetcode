class Solution:
    def mostVisited(self, n: int, rounds: List[int]) -> List[int]:
        start = rounds[0]
        end = rounds[-1]
        if start == end:
            return [start]
        if start < end:
            return [num for num in range(start, end + 1)]
        return [num for num in range(1, end + 1)] + [num for num in range(start, n + 1)]