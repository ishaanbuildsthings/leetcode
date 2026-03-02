import itertools

class Solution:
    def isSolvable(self, words: List[str], result: str) -> bool:
        
        allC = set()
        for w in words:
            for c in w:
                allC.add(c)
        for c in result:
            allC.add(c)
        
        allC = sorted(allC)

        #  SEND
        #  MORE
        # MONEY

        words.append(result)
        rows = len(words)
        maxCol = max(map(len, words))

        cToV = {} # maps letter -> mapped value

        def backtrack(row, col, carryAndSum):
            if col == maxCol:
                return carryAndSum == 0
            if row == len(words):
                # if we ran out of words, as long as we have a carry that is divisible by the next digit we are good
                # for instance 30+40 (so basically 3+4) is 7 but if we carry a 7 we can never neutralize that since all future numbers operate on a larger magnitude
                # but 3+4+3 = 100 basically and that can be neutralized
                if carryAndSum % 10 == 0:
                    return backtrack(0, col + 1, carryAndSum // 10)
                return False

            w = words[row]
            # if the word is too small we skip it
            if len(w) <= col:
                return backtrack(row + 1, col, carryAndSum)
            
            c = w[~col]
            # if the letter is in the map we take it and move on
            if c in cToV:
                gain = cToV[c]
                # i tried to prevent setting leading 0s earlier but it is still tricky in cases like words = [A, A] result = [AA] because the A from the word sets a leading 0 in result
                if gain == 0 and col == len(w) - 1 and len(w) > 1:
                    return False
                # subtract for result word
                if row == rows - 1:
                    gain = -1 * gain
                return backtrack(row + 1, col, carryAndSum + gain)
            
            # if it is not, we should try all possible numbers
            allNumbers = set(cToV.values())
            for number in range(10):
                # never assign a letter that would force a leading 0
                if (c == w[0] and number == 0 and len(w) > 1):
                    continue
                if number in allNumbers:
                    continue
                cToV[c] = number
                gain = number
                if row == rows - 1:
                    gain *= -1
                if backtrack(row + 1, col, carryAndSum + gain):
                    return True
                del cToV[c]

            return False
        
        return backtrack(0, 0, 0)
        
                

                
