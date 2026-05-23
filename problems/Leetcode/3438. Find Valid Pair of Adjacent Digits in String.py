class Solution:
    def findValidPair(self, s: str) -> str:
        c = Counter(s)
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                continue
            c1 = c[s[i]]
            c2 = c[s[i+1]]
            if c1 == int(s[i]) and c2 == int(s[i+1]):
                return s[i:i+2]
        return ''