class Solution:
    def maxRepOpt1(self, text: str) -> int:
        n = len(text)
        ri = [1] * n
        for i in range(len(text) - 2, -1, -1):
            if text[i] == text[i + 1]:
                ri[i] = ri[i + 1] + 1
        res = 0
        c = Counter(text)
        for i in range(n):
            s1 = ri[i]
            r = i + s1 - 1
            if r + 2 < len(text) and text[r + 2] == text[i]:
                s2 = ri[r + 2]
                s1 += s2
            if s1 < c[text[i]]:
                s1 += 1
            res = max(res, s1)
        return res