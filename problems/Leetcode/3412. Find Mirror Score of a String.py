class Solution:
    def calculateScore(self, s: str) -> int:
        unmarked = defaultdict(list) # maps letter to list of unmarked indices
        
        def getMirror(char):
            return chr(219 - ord(char)) if char.isalpha() else char
        
        res = 0
        
        for i in range(len(s)):
            c = s[i]
            mirror = getMirror(c)
            if not unmarked[mirror]:
                unmarked[c].append(i)
                continue
            lastIdx = unmarked[mirror].pop()
            res += i - lastIdx
        
        return res