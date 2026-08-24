class Solution:
    def isOneEditDistance(self, s: str, t: str) -> bool:
        if abs(len(s) - len(t)) > 1:
            return False
        if s == t:
            return False

        if len(s) > len(t):
            return self.isOneEditDistance(t, s)
        
        if len(s) == len(t):
            diffs = sum(s[i] != t[i] for i in range(len(s)))
            return diffs == 1
        
        # s is shorter

        for i in range(len(s)):
            if s[i] != t[i]:
                # can do O(1) space style
                return s[i:] == t[i + 1:]

        
        return True


