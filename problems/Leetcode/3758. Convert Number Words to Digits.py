class Solution:
    def convertNumber(self, s: str) -> str:
        words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        res = []
        i = 0
        while i < len(s):
            found = False
            for idx, w in enumerate(words):
                n = len(w)
                if s[i:i+n] == w:
                    res.append(idx)
                    i += n
                    found = True
                    break
            if found:
                continue
            i += 1
        
        return ''.join(map(str, res))