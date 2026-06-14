class Solution:
    def maxRatings(self, units: List[List[int]]) -> int:
        for i in range(len(units)):
            units[i].sort()
        res = sum(
            min(unit) for unit in units
        )

        # print(f'init res: {res}')

        pfMin = []
        curr = inf
        for unit in units:
            # we never sac singles
            if len(unit) == 1:
                pfMin.append(curr)
                continue
            mn = min(unit)
            curr = min(curr, mn)
            pfMin.append(curr)

        suffMin = [inf] * len(units)
        curr = inf
        for i in range(len(units) - 1, -1, -1):
            if len(units[i]) == 1:
                continue
            mn = min(units[i])
            curr = min(curr, mn)
            suffMin[i] = curr



        pfSum = [] # holds sum of second mins
        curr = 0
        for unit in units:
            if len(unit) == 1:
                curr += unit[0] # we keep the only unit in this device actually
                pfSum.append(curr)
                continue
            curr += unit[1]
            pfSum.append(curr)


        suffSum = [0] * len(units)
        curr = 0
        for i in range(len(units) - 1, -1, -1):
            if len(units[i]) == 1:
                curr += units[i][0]
                suffSum[i] = curr
                continue
            curr += units[i][1]
            suffSum[i] = curr


        # print(pfSum)
        # print(suffSum)


        for i in range(len(units)):
            # this is the drain unit
            beforeSmall = pfMin[i - 1] if i else inf
            afterSmall = suffMin[i + 1] if i + 1 < len(units) else inf
            smallHere = min(beforeSmall, afterSmall, min(units[i]))

            beforeSum = pfSum[i - 1] if i else 0
            afterSum = suffSum[i + 1] if i + 1 < len(units) else 0

            score = smallHere + beforeSum + afterSum

            res = max(res, score)

        return res
            
            
            