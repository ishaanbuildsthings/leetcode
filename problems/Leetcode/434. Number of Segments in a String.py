class Solution:
    def countSegments(self, s: str) -> int:
        res = 0
        seenNonEmpty = False
        for i in range(len(s)):
            if s[i] == ' ' and not seenNonEmpty:
                continue

            if i and s[i - 1] == ' ' and s[i] != ' ' and seenNonEmpty:
                res += 1

            if s[i] != ' ':
                seenNonEmpty = True
        if not any(s[i] != ' ' for i in range(len(s))):
            return 0
        return res + 1