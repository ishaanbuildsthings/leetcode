class Solution:
    def minimumCost(self, s: str) -> int:
        n = len(s)
        pfOnes = [0] * n
        pfZeroes = [0] * n # min cost to set the prefix 0...i to all 0s
        if s[0] == '0':
            pfOnes[0] = 1
        else:
            pfZeroes[0] = 1
        
        for i in range(1, n):
            costOp = i + 1
            v = int(s[i])
            if v == 1:
                pfOnes[i] = pfOnes[i - 1]
                pfZeroes[i] = costOp + pfOnes[i - 1]
            else:
                pfZeroes[i] = pfZeroes[i - 1]
                pfOnes[i] = costOp + pfZeroes[i - 1]
        

        suffOnes = [0] * n
        suffZeroes = [0] * n
        if s[-1] == '0':
            suffOnes[-1] = 1
        else:
            suffZeroes[-1] = 1
        for i in range(n - 2, -1, -1):
            costOp = n - i
            v = int(s[i])
            if v == 1:
                suffOnes[i] = suffOnes[i + 1]
                suffZeroes[i] = costOp + suffOnes[i + 1]
            else:
                suffZeroes[i] = suffZeroes[i + 1]
                suffOnes[i] = costOp + suffZeroes[i + 1]
        
        res = inf
        for i in range(n):
            # make a string of ones
            suffOne = suffOnes[i]
            pfOne = 0 if not i else pfOnes[i - 1]
            totOne = pfOne + suffOne

            # make a string of 0s
            suffZ = suffZeroes[i]
            pfZ = 0 if not i else pfZeroes[i-1]
            totZ = suffZ + pfZ

            res = min(res, totOne, totZ)
        
        return res

        
