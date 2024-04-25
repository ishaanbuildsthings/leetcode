# https://leetcode.com/problems/robot-return-to-origin/description/
# difficulty: easy

# Solution, O(n) time O(1) space
class Solution:
    def judgeCircle(self, moves: str) -> bool:
        counts = Counter(moves)
        return counts['U'] == counts['D'] and counts['L'] == counts['R']