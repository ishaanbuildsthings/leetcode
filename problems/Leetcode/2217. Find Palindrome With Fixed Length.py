class Solution:
    def kthPalindrome(self, queries: List[int], intLength: int) -> List[int]:
        if intLength == 1:
            maxPalindromes = 9
        else:
            insideDigits = intLength - 2
            insideChoices = insideDigits // 2
            if intLength % 2:
                insideChoices += 1
            maxPalindromes = 9 * (10**insideChoices)
                
        res = []
        for k in queries:
            if k > maxPalindromes:
                res.append(-1)
                continue
            
            # handle 1 length separately it is easier
            if intLength == 1:
                res.append(k)
                continue
            
            resHere = [-1] * intLength
            passed = 0

            # loop through non middle digits
            for i in range(intLength // 2):
                outsidePassed = 2 * (i + 1)
                insideDigits = intLength - outsidePassed

                # numbers we can actually toggle
                insideChoices = insideDigits // 2
                if intLength % 2:
                    insideChoices += 1
                
                # number of palindromes we can make with the inside digits (leading 0 allowed)
                insideZeroPals = 10**insideChoices
                remain = k - passed - 1
                fullPasses = remain // insideZeroPals

                if i == 0:
                    resHere[i] = fullPasses + 1
                    resHere[-1] = fullPasses + 1
                else:
                    resHere[i] = fullPasses
                    resHere[-(i + 1)] = fullPasses
                
                passed += insideZeroPals * fullPasses

            # set the middle digit
            if intLength % 2 == 1:
                middlePos = (intLength // 2)
                remain = k - passed
                resHere[middlePos] = remain - 1                        

            res.append(int(''.join(str(x) for x in resHere)))
        
        return res





