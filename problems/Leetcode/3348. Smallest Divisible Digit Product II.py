class Solution:
    def smallestNumber(self, num: str, t: int) -> str:
        n = len(num)

        tFacs = Counter() # prime factors, if any >= 11 we fail immediately
        for x in [2, 3, 5, 7]:
            while t % x == 0:
                tFacs[x] += 1
                t //= x
        if t != 1:
            return '-1'

        req = (tFacs[2], tFacs[3], tFacs[5], tFacs[7])
        numberToPrimesUsed = {
            0 : (0,0,0,0),
            1: (0,0,0,0), 2: (1,0,0,0), 3: (0,1,0,0), 4: (2,0,0,0), 5: (0,0,1,0), 6: (1,1,0,0), 7: (0,0,0,1), 8: (3,0,0,0), 9: (0,2,0,0)
        }

        def fewestDigits(twos, threes, fives, sevens):
            required = fives + sevens # cannot compress these

            # we should always group up three 2s
            groupTwos = twos // 3
            required += groupTwos

            twos -= groupTwos * 3

            # now we have at most two 2s left, and also 3s

            if twos == 2:
                required += 1 # use a 4
                required += ceil(threes / 2)
                return required
            if twos == 1:
                required += 1 # use a 2 or a 6
                threes = max(0, threes - 1)
                required += ceil(threes / 2) # use 9s
                return required
            return required + ceil(threes / 2) # use 9s

        # i require `owed` and use `digit`, what do i owe now?
        def payWithDigit(owed, digit):
                    twosOwed, threesOwed, fivesOwed, sevensOwed = owed
                    twos, threes, fives, sevens = numberToPrimesUsed[digit]
                    return (
                            max(0, twosOwed - twos),
                            max(0, threesOwed - threes),
                            max(0, fivesOwed - fives),
                            max(0, sevensOwed - sevens)
                        )

        pf = [[0] * 4 for _ in range(len(num))]  # 2s 3s 5s 7s
        for i in range(len(num)):
            for j in range(4):
                pf[i][j] = (pf[i-1][j] if i else 0) + numberToPrimesUsed[int(num[i])][j]

        first0 = num.find('0')
        startI = first0 if first0 != -1 else len(num) - 1

        # use the number itself
        if first0 == -1 and all(pf[n-1][k] >= req[k] for k in range(4)):
            return num

        # slots is spots to fill, owed is a tuple of size 4
        def fillSuff(slots, owed):
            minDigits = fewestDigits(*owed)
            # pad 1s
            out = ['1'] * (slots - minDigits)
            # we loop on the leftmost digit first, trying to make it as small as possible
            for remainToFiill in range(minDigits, 0, -1):
                # if we put a digit here, can we still fill the suffix? if so use this smallest one
                for digit in range(1, 10):
                    remaining = payWithDigit(owed, digit)
                    if fewestDigits(*remaining) <= remainToFiill - 1:
                        out.append(str(digit))
                        owed = remaining
                        break
            return ''.join(out)

        for i in range(startI, -1, -1):
            suffixSlots = n - 1 - i
            prefixPrimes = pf[i-1] if i else (0, 0, 0, 0)
            owedAfterPrefix = tuple(max(0, req[k] - prefixPrimes[k]) for k in range(4))
            # try bumping up this digit
            for digit in range(int(num[i]) + 1, 10):
                owedAfterBump = payWithDigit(owedAfterPrefix, digit)
                if fewestDigits(*owedAfterBump) <= suffixSlots:
                    return num[:i] + str(digit) + fillSuff(suffixSlots, owedAfterBump)
        
        return fillSuff(max(n + 1, fewestDigits(*req)), req)
        