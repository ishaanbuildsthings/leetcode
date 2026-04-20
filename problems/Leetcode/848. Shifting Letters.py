class Solution:
    def shiftingLetters(self, s: str, shifts: List[int]) -> str:
        n = len(s)
        res = [None] * n
        sweep = [0] * (n + 1)
        for i in range(len(shifts)):
            sweep[0] += shifts[i]
            sweep[i + 1] -= shifts[i]
        
        def apply(c, shifts):
            shifts %= 26
            initV = ord(c)
            initV += shifts
            zV = ord('z')
            if initV > zV:
                initV -= 26
            return chr(initV)
        
        curr = 0
        for i in range(n):
            curr += sweep[i]
            res[i] = apply(s[i], curr)
        
        return ''.join(res)
