class Solution:
    def makeStringsEqual(self, s: str, target: str) -> bool:
        if s == target:
            return True
        return '1' in target and '1' in s