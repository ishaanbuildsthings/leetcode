class Solution:
    def diStringMatch(self, s: str) -> List[int]:
        l = 0
        r = len(s)
        res = []
        for c in s:
            if c == 'I':
                res.append(l)
                l += 1
            else:
                res.append(r)
                r -= 1
        res.append(l)
        return res