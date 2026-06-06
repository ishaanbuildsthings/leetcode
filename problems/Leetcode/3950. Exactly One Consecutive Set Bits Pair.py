class Solution:
    def consecutiveSetBits(self, n: int) -> bool:
        s = bin(n)[2:]
        score = 0
        for i in range(len(s) - 1):
            if s[i] == '1' and s[i+1] == '1':
                score += 1
        return score == 1