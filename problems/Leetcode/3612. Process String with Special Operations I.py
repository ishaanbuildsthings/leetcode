class Solution:
    def processStr(self, s: str) -> str:
        res = []
        for i, c in enumerate(s):
            if c.isalpha():
                res.append(c)
                continue
            
            if c == '*':
                if res:
                    res.pop()
                continue

            if c == '#':
                res = res + res
                continue

            if c == '%':
                res = res[::-1]

        return ''.join(res)
            