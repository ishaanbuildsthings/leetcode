class Solution:
    def findLUSlength(self, a: str, b: str) -> int:
        return (max(len(a), len(b)) if len(a) != len(b)
            else len(a) if a != b else -1)