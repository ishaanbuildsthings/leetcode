class Solution:
    def minBishopMoves(self, source: list[int], target: list[int]) -> int:
        def color(r, c):
            return (r + c) % 2
        if color(*source) != color(*target):
            return -1
        if source[1] - source[0] == target[1] - target[0]:
            return 1
        if sum(source) == sum(target):
            return 1
        return 2