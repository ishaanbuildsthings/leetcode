class Solution:
    def kthDigit(self, k: int) -> int:
        
        mp = { # maps number length to # of numbers with that length
            1 : 9,
            2 : 90,
            3 : 900
        }
        for v in range(4, 15):
            mp[v] = 9 * (10**(v-1))
        
        # how many numbers are fully contained before k?
        remain = k - 1
        numbersContained = 0
        for currWidth in range(1, 15):
            amount = mp[currWidth]
            allowedToTake = min(remain // currWidth, amount)
            numbersContained += allowedToTake
            remain -= (allowedToTake * currWidth)

        number = numbersContained + 1 # the number we live at before accounting for reversal
        digit = remain + 1 # we want the `digit-th` digit of `number`
        surplus = number % 10
        oppositeNumber = number + 9 - surplus - surplus
        
        answer = int(str(number)[digit-1])
        oppositeAnswer = int(str(oppositeNumber)[digit-1])

        # contain 0-8 means we are not in reversal
        # contain 9-18 means we are in reversal
        # contain 19-28 means we are not in reversal
        # etc

        inReversal = ((numbersContained + 1) // 10) % 2 == 1

        return oppositeAnswer if inReversal else answer

