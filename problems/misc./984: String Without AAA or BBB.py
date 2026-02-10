class Solution:
    def strWithout3a3b(self, a: int, b: int) -> str:
        res = []
        while a > 0 or b > 0:
            if a > b:
                # forced to put b
                if len(res) >= 2 and res[-1] == 'a' and res[-2] == 'a':
                    b -= 1
                    res.append('b')
                else:
                    a -= 1
                    res.append('a')
            else:
                if len(res) >= 2 and res[-1] == 'b' and res[-2] == 'b':
                    a -= 1
                    res.append('a')
                else:
                    b -= 1
                    res.append('b')
        return ''.join(res)