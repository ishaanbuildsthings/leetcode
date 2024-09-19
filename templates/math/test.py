def countSteppingNumbers(low, high):

    # @cache
    def dp(i, prev, isTight, strNum, isLeadingZero):
        # print(f'dp called on i={i} prev={prev} isTight={isTight} strNum={strNum} isLeadingZero={isLeadingZero}')
        if i == len(strNum):
            return ['']

        nextDigits = []

        if prev == None:
            for nextDigit in range(int(strNum[i]) + 1):
                nextDigits.append(nextDigit)
        elif isLeadingZero:
            for nextDigit in range(10):
                nextDigits.append(nextDigit)
        else:
            upperBound = int(strNum[i]) if isTight else 9
            lowerBound = 0
            if prev - 1 >= lowerBound:
                nextDigits.append(prev - 1)
            if prev + 1 <= upperBound:
                nextDigits.append(prev + 1)

        resThis = []
        for nextDigit in nextDigits:
            newIsTight = isTight and str(nextDigit) == strNum[i]
            newIsLeadingZero = isLeadingZero and nextDigit == 0
            nextDp = dp(i + 1, nextDigit, newIsTight, strNum, newIsLeadingZero)
            for suffix in nextDp:
                resThis.append(str(nextDigit) + suffix)

        return resThis

    highDp = dp(0, None, True, str(high), True)
    # print(highDp)
    return [int(string) for string in highDp if int(string) >= low]

print(countSteppingNumbers(0, 2000000000))
