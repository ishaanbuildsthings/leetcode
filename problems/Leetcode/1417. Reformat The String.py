class Solution:
    def reformat(self, s: str) -> str:
        # can use counters instead lol
        letters = []
        digits = []
        for c in s:
            if c.isdigit():
                digits.append(c)
            else:
                letters.append(c)
        
        bigger = letters if len(letters) >= len(digits) else digits
        smaller = letters if bigger == digits else digits

        resArr = []
        curr = bigger
        while curr:
            resArr.append(curr.pop())
            curr = smaller if curr == bigger else bigger
        
        return ''.join(resArr) if len(resArr) == len(s) else ''
            