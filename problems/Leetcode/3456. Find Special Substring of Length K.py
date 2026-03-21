class Solution:
    def hasSpecialSubstring(self, s: str, k: int) -> bool:
        for l in range(len(s)):
            rightEdge = l + k - 1
            if rightEdge >= len(s):
                break
            substring = s[l:l+k]
            set2 = set(substring)
            if len(set2) > 1:
                continue
            character = s[l]
            if l > 0:
                before = s[l-1]
                if before == character:
                    continue
            if rightEdge < len(s) - 1:
                after = s[rightEdge + 1]
                if after == character:
                    continue
            return True
        return False