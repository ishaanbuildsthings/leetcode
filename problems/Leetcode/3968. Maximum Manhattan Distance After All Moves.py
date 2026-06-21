class Solution:
    def maxDistance(self, moves: str) -> int:
        c = Counter(moves)
        UP = abs(c['U'] - c['D'])
        LEFT = abs(c['L'] - c['R'])
        unknown = c['_']
        return UP + LEFT + unknown