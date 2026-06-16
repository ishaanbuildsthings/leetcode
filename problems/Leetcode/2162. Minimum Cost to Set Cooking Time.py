class Solution:
    def minCostSetTime(self, startAt: int, moveCost: int, pushCost: int, targetSeconds: int) -> int:

        # BAD SOLUTION, just analyze the few options lol

        def microwaveStrToSeconds(microwaveStr):
            prependedStr = microwaveStr.zfill(4)
            minutes = int(prependedStr[:2])
            seconds = int(prependedStr[2:])
            totalSeconds = minutes * 60 + seconds
            return totalSeconds

        def dfs(currentInputStr):
            # base case, we have the exact number
            if microwaveStrToSeconds(currentInputStr) == targetSeconds:
                return 0
            # early prune
            if microwaveStrToSeconds(currentInputStr) > targetSeconds:
                return float('inf')
            
            # if we run out of valid options
            if len(currentInputStr) == 4:
                return float('inf')

            resThis = float('inf')
            
            for nextDigit in range(10):
                costToTravel = 0 if currentInputStr == '' and nextDigit == startAt else moveCost if currentInputStr == '' else 0 if int(currentInputStr[-1]) == nextDigit else moveCost
                costToClick = costToTravel + pushCost
                resThis = min(resThis, costToClick + dfs(currentInputStr + str(nextDigit)))
            
            return resThis
        
        return dfs('')



