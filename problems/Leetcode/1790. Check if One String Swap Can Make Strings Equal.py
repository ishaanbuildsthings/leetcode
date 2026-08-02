class Solution:
    def areAlmostEqual(self, s1: str, s2: str) -> bool:
        mismatch = [i for i in range(len(s1)) if s1[i] != s2[i]]
        if len(mismatch) > 2 or len(mismatch) == 1:
            return False
        if not len(mismatch):
            return True
        return s1[mismatch[0]] == s2[mismatch[1]] and s1[mismatch[1]] == s2[mismatch[0]]
        