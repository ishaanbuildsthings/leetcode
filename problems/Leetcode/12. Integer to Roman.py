class Solution:
    def intToRoman(self, num: int) -> str:
        resArr = []

        def handleRepeatedCase(valueSize, symbol, remain):
            amountOfThatValue = (remain // valueSize)
            resArr.append(symbol * amountOfThatValue)
            tabulate(remain - (valueSize * amountOfThatValue))

        def tabulate(remain):

            if remain == 0:
                return

            if remain <= 3:
                resArr.append('I' * remain)
                return
            
            if remain == 4:
                resArr.append('IV')
                return
            
            # handle thousands
            if remain >= 1000:
                handleRepeatedCase(1000, 'M', remain)
                return
            # handle 900
            if remain >= 900:
                resArr.append('CM')
                tabulate(remain - 900)
                return

            # handle 500s
            if remain >= 500:
                handleRepeatedCase(500, 'D', remain)
                return
            # handle 400
            if remain >= 400:
                resArr.append('CD')
                tabulate(remain - 400)
                return
            
            # handle 100s
            if remain >= 100:
                handleRepeatedCase(100, 'C', remain)
                return
            # handle 90
            if remain >= 90:
                resArr.append('XC')
                tabulate(remain - 90)
                return
            
            # handle 50s
            if remain >= 50:
                handleRepeatedCase(50, 'L', remain)
                return
            # handle 40
            if remain >= 40:
                resArr.append('XL')
                tabulate(remain - 40)
                return
            
            # handle 10s
            if remain >= 10:
                handleRepeatedCase(10, 'X', remain)
                return
            # handle 9
            if remain >= 9:
                resArr.append('IX')
                tabulate(remain - 9)
                return
            
            # handle 5s
            if remain >= 5:
                handleRepeatedCase(5, 'V', remain)
                return
        
        tabulate(num)    
        
        return ''.join(resArr)