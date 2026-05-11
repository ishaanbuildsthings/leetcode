class Solution:
    def isSumEqual(self, firstWord: str, secondWord: str, targetWord: str) -> bool:
        
        def make(s):
            tot = 0
            for i in range(len(s) - 1, -1, -1):
                power = len(s) - i - 1
                tot += (ord(s[i]) - ord('a')) * 10**power
            return tot
        
        return make(firstWord) + make(secondWord) == make(targetWord)
