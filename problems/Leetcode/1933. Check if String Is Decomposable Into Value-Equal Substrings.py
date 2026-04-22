class Solution:
    def isDecomposable(self, s: str) -> bool:
        div3 = 0
        req2 = 0
        streak = 1
        curr = s[0]
        for i in range(1, len(s)):
            v = s[i]
            if v == curr:
                streak += 1
                continue
            if streak == 1:
                return False
            curr = v
            if streak % 3 == 0:
                div3 += 1
                streak = 1
                continue
            if (streak - 2) % 3 == 0:
                req2 += 1
                streak = 1
                if req2 > 1:
                    return False
                continue
            return False
        if streak == 1:
            return False
        if (streak - 2) % 3 == 0:
            req2 += 1
        if req2 > 1 or req2 == 0:
            return False
        return True
