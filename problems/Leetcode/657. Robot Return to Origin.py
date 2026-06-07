class Solution:
    def judgeCircle(self, moves: str) -> bool:
        counts = Counter(moves)
        return counts['U'] == counts['D'] and counts['L'] == counts['R']