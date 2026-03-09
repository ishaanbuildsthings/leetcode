class Solution:
    def minFlips(self, s: str) -> int:
        
        d = s + s
        res = inf
        n = len(s)
        mismatchesAgainst0AsFirstIndex = 0
        for i in range(n):
            desired = i % 2
            if int(s[i]) != desired:
                mismatchesAgainst0AsFirstIndex += 1

        mismatchesAgainst0AsSecondIndex = 0
        for i in range(n):
            desired = (i % 2) ^ 1
            if int(s[i]) != desired:
                mismatchesAgainst0AsSecondIndex += 1
        
        res = min(mismatchesAgainst0AsFirstIndex, mismatchesAgainst0AsSecondIndex)
        for r in range(n, len(d)):
            gained = int(d[r])
            lost = int(d[r - n])

            desired0 = r % 2
            desiredLost0 = (r - n) % 2
            if gained != desired0:
                mismatchesAgainst0AsFirstIndex += 1
            if lost != desiredLost0:
                mismatchesAgainst0AsFirstIndex -= 1


            desired1 = (r % 2) ^ 1
            desiredLost1 = desiredLost0 ^ 1
            if gained != desired1:
                mismatchesAgainst0AsSecondIndex += 1
            if lost != desiredLost1:
                mismatchesAgainst0AsSecondIndex -= 1
            
            res = min(res, mismatchesAgainst0AsFirstIndex, mismatchesAgainst0AsSecondIndex)
        
        return res
            

