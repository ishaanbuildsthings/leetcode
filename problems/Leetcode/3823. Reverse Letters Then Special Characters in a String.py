class Solution:
    def reverseByType(self, s: str) -> str:
        lowers = []
        specials = []
        for v in s:
            if v.isalpha():
                lowers.append(v)
            else:
                specials.append(v)
        print(lowers)

        res = [None] * len(s)

        i = len(lowers) - 1
        j = len(specials) - 1
        for k in range(len(s)):
            v = s[k]
            if v.isalpha():
                res[k] = lowers[i]
                i -= 1
            else:
                res[k] = specials[j]
                j -= 1
        
        return ''.join(res)