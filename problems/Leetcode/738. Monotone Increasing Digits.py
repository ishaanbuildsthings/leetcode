class Solution:
    def monotoneIncreasingDigits(self, n: int) -> int:
        strNum = str(n)
        choice = {} # maps a dp state -> selected digit
        nextState = {} # maps a dp state -> nextState

        # NOTE, thi is 10*10*logN time complexity, but there is probably faster, see the better solution

        @cache
        def dp(i, isTight, prevDigit):
            # base case
            if i == len(strNum):
                return True # returns if the DP setup is doable
            
            upperBoundary = int(strNum[i]) if isTight else 9
            for nextDigit in range(upperBoundary, prevDigit - 1, -1):
                newIsTight = isTight and nextDigit == upperBoundary
                nextDp = dp(i + 1, newIsTight, nextDigit)
                if nextDp:
                    choice[(i, isTight, prevDigit)] = nextDigit
                    nextState[(i, isTight, prevDigit)] = (i + 1, newIsTight, nextDigit)
                    return True
            
            return False
        
        dp(0, True, 0)

        res = []
        currTup = (0, True, 0)

        while True:
            if not currTup in choice:
                return int(''.join(res))
            picked = choice[currTup]
            res.append(str(picked))
            nextTup = nextState[currTup]
            currTup = nextTup
        