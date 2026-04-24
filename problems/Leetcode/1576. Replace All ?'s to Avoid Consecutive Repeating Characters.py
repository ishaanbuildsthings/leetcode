class Solution:
    def modifyString(self, s: str) -> str:
        res = []
        for i in range(len(s)):
            if s[i] != '?':
                res.append(s[i])
                continue
            left = res[i - 1] if i else '#'
            right = s[i + 1] if i + 1 < len(s) else '#'
            nv = 'a' if 'a' not in [left, right] else 'b' if 'b' not in [left, right] else 'c'
            res.append(nv)
        return ''.join(res)