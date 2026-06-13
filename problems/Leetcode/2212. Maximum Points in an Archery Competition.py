class Solution:
    def maximumBobPoints(self, numArrows: int, aliceArrows: List[int]) -> List[int]:
        choice = {}
        @cache
        def dp(arrowsLeft, scoreSection):
            t = (arrowsLeft, scoreSection)
            if scoreSection == 12:
                return 0
            bestScore = 0
            
            ifDontTry = dp(arrowsLeft, scoreSection + 1)

            if arrowsLeft > aliceArrows[scoreSection]:
                ifTry = scoreSection + dp(arrowsLeft - aliceArrows[scoreSection] - 1, scoreSection + 1)
            else:
                ifTry = 0
            
            if ifDontTry >= ifTry:
                choice[t] = False
            else:
                choice[t] = True
            
            return max(ifTry, ifDontTry)
        
        ans = dp(numArrows, 0)

        res = []
        arrows = numArrows
        currScore = 0
        for section in range(12):
            if choice[(arrows, section)] == True:
                arrowsSpent = aliceArrows[section] + 1
                arrows -= arrowsSpent
                currScore += aliceArrows[section]
                res.append(arrowsSpent)
            else:
                res.append(0)
        if sum(res) != numArrows:
            res[0] += numArrows - sum(res)
        return res
