class Solution:
    def isAdjacentDiffAtMostTwo(self, s: str) -> bool:
        for i in range(len(s) - 1):
            a = int(s[i])
            b = int(s[i+1])
            diff = abs(a-b)
            if diff > 2:
                return False
        return True