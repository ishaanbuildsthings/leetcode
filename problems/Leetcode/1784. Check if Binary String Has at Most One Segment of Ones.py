class Solution:
    def checkOnesSegment(self, s: str) -> bool:
        seenZ = False
        for i in range(1, len(s)):
            if s[i] == '0':
                seenZ = True
            elif s[i] == '1':
                if seenZ:
                    return False
        return True