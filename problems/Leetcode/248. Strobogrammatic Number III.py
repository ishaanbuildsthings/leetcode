ROT = {0:0, 1:1, 6:9, 8:8, 9:6}
def flip(s): return ''.join(str(ROT[int(c)]) for c in reversed(s))

class Solution:
    def strobogrammaticInRange(self, low: str, high: str) -> int:
        L = len(low)
        R = len(high)

        res = 0

        for sz in range(L + 1, R):
            if sz % 2:
                pairs = sz // 2
                outerPairWays = 4 # (1,1) (8,8) (6,9) (9,6)
                innerPairs = pairs - 1
                innerPairWays = 5**innerPairs # (0, 0) (1,1) (8,8) (6,9) (9,6)
                middleOptions = 3 if sz != 1 else 1
                totalWays = outerPairWays * innerPairWays * middleOptions
                res += totalWays
            else:
                pairs = sz // 2
                outerPairWays = 4 # (1,1) (8,8) (6,9) (9,6)
                innerPairs = pairs - 1
                innerPairWays = 5**innerPairs
                totalWays = outerPairWays * innerPairWays
                res += totalWays
        
        # compute amounts for numbers exactly length L and >= low
        @cache
        def dpLow(i, lowTight):
            # base case at a center
            if L % 2 == 1 and i == L // 2:
                digit = int(low[i])
                # if we dropped on the prefix safely, we can use any center digit
                if not lowTight:
                    return 3
                if digit <= 0:
                    return 3
                if digit <= 1:
                    return 2
                if digit <= 8:
                    return 1
                return 0
            # base case, finished evens
            if L % 2 == 0 and i == L // 2:
                if not lowTight:
                    return 1
                # if we were tight we need to make sure the string is valid
                number = low[:L//2] + flip(low[:L//2])
                if int(number) >= int(low):
                    return 1
                return 0
            
            resHere = 0
            d = int(low[i])
            DIGITS = [0, 1, 6, 8, 9] if i != 0 else [1, 6, 8, 9]
            for digit in DIGITS:
                if digit < d and lowTight:
                    continue
                nlowTight = lowTight and digit == d
                resHere += dpLow(i + 1, nlowTight)
            
            return resHere
        
        ansLow = dpLow(0, True)

        @cache
        def dpHigh(i, highTight):
            if R % 2 == 1 and i == R // 2:
                if not highTight:
                    return 3
                score = 0
                digit = int(high[i])
                for d in [0, 1, 8]:
                    if d > digit:
                        continue
                    if d < digit:
                        score += 1
                        continue
                    number = int(high[:R//2] + high[i] + flip(high[:R//2]))
                    if number <= int(high):
                        score += 1
                return score
            if R % 2 == 0 and i == R // 2:
                if not highTight:
                    return 1
                number = high[:R//2] + flip(high[:R//2])
                if int(number) <= int(high):
                    return 1
                return 0
            d = int(high[i])
            DIGITS = [0, 1, 6, 8, 9] if i != 0 else [1, 6, 8, 9]
            resHere = 0
            for digit in DIGITS:
                if digit > d and highTight:
                    continue
                nhighTight = highTight and digit == d
                resHere += dpHigh(i + 1, nhighTight)
            return resHere

        @cache
        def dpBoth(i, ltight, htight):
            if L % 2 and i == L // 2:
                if not ltight and not htight:
                    return 3 # 0, 1, 8

                if htight and not ltight:
                    up = int(high[i])
                    score = 0
                    for d in [0, 1, 8]:
                        if d > up:
                            continue
                        if d < up:
                            score += 1
                            continue
                        # if this digit exactly matches the upper boundary we need to see if this number is valid
                        number = int(high[:R//2] + str(d) + flip(high[:R//2]))
                        if number <= int(high):
                            score += 1
                    return score
                
                if ltight and not htight:
                    down = int(low[i])
                    score = 0
                    for d in [0, 1, 8]:
                        if d < down:
                            continue
                        if d > down:
                            score += 1
                            continue
                        number = int(low[:L//2] + str(d) + flip(low[:L//2]))
                        if number >= int(low):
                            score += 1
                    return score
                
                # both ltight and htight
                P = low[:L//2]
                lo, hi = int(low), int(high)
                score = 0
                for d in [0,1,8]:
                    num = int(P + str(d) + flip(P))
                    if lo <= num <= hi:
                        score += 1
                return score

            if L % 2 == 0 and i == L // 2:
                if not ltight and not htight:
                    return 1
                if ltight and not htight:
                    number = int(low[:L//2] + flip(low[:L//2]))
                    if number >= int(low):
                        return 1
                    return 0
                if htight and not ltight:
                    number = int(high[:R//2] + flip(high[:R//2]))
                    if number <= int(high):
                        return 1
                    return 0
                # both tight
                number = int(low[:L//2] + flip(low[:L//2]))
                if number >= int(low) and number <= int(high):
                    return 1
                return 0
            
            resHere = 0
            dlow = int(low[i])
            dhigh = int(high[i])
            DIGITS = [0, 1, 6, 8, 9] if i != 0 else [1, 6, 8, 9]
            for d in DIGITS:
                if ltight and d < dlow:
                    continue
                if htight and d > dhigh:
                    continue
                nlt = ltight and d == dlow
                nht = htight and d == dhigh
                resHere += dpBoth(i + 1, nlt, nht)
            
            return resHere


        if R == L:
            return dpBoth(0, True, True)

        ansHigh = dpHigh(0, True)
        
        return res + ansLow + ansHigh
