from copy import copy
class Solution:
    def lexPalindromicPermutation(self, s: str, target: str) -> str:
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        n = len(target)

        @cache
        def pfS(letter, i):
            if i == -1:
                return 0
            score = int(s[i] == letter)
            return score + pfS(letter, i - 1)

        @cache
        def pfT(letter, i):
            if i == -1:
                return 0
            score = int(target[i] == letter)
            return score + pfT(letter, i - 1)
        
        def queryS(l, r, letter):
            return pfS(letter, r) - pfS(letter, l - 1)
        
        def queryT(l, r, letter):
            return pfT(letter, r) - pfT(letter, l - 1)
        
        leftHalfS = Counter()
        for i in range(len(s) // 2):
            leftHalfS[s[i]] += 1
        
        leftHalfT = Counter()
        for i in range(len(target) // 2):
            leftHalfT[target[i]] += 1
        
        allS = Counter(s)
        ODDS_S = sum(x % 2 for x in allS.values())


        for i in range(n - 1, -1, -1):
            isLeft = i < n // 2
            isMiddle = n % 2 == 1 and i == n // 2
            isRight = not isLeft and not isMiddle
            c = target[i]
            greaterLetters = [x for x in ABC if x > c]

            if isMiddle:
                # bump up the middle target letter, use the full left and right halves of target
                leftT = copy(leftHalfT)
                for letter in leftT:
                    leftT[letter] *= 2
                for bumped in greaterLetters:
                    leftT[bumped] += 1
                    if leftT == allS:
                        return target[:i] + bumped + target[:i][::-1]
                    leftT[bumped] -= 1
            
            elif isLeft:
                fixed = Counter()
                for letter in ABC:
                    cnt = 2 * pfT(letter, i - 1)
                    if cnt:
                        fixed[letter] = cnt

                if fixed - allS:
                    continue
                # we can make the prefix and suffix before i (twice over, for the ending too)

                remainS = allS - fixed
                for bumped in greaterLetters:
                    if remainS[bumped] < 2:
                        continue

                    remainS[bumped] -= 2
                    if ODDS_S > 1 or ODDS_S == 1 and n % 2 == 0:
                        remainS[bumped] += 2
                        continue

                    # we can make one
                    res = [None] * n
                    for j in range(i):
                        res[j] = target[j]
                        res[~j] = target[j]
                    res[i] = bumped
                    res[~i] = bumped
                    for j in range(i + 1, (n + 1) // 2):
                        isMid = j == n // 2 and n % 2 == 1
                        for letter in ABC:
                            req = 1 if isMid else 2
                            if remainS[letter] >= req:
                                remainS[letter] -= req
                                res[j] = letter
                                res[~j] = letter
                                break
                            else:
                                continue
                    return ''.join(res)
            
            elif isRight:
                mirrorI = n - i - 1
                bumped = target[mirrorI]
                if bumped <= c:
                    continue

                fixed = copy(leftHalfT)
                for letter in fixed:
                    fixed[letter] *= 2

                remainS = allS - fixed
                odds = sum(v % 2 for v in remainS.values())
                if sum(remainS.values()) != n % 2 or odds > n % 2:
                    continue

                mid = next((letter for letter in ABC if remainS[letter]), '')
                forced = target[:n // 2] + mid + target[:n // 2][::-1]
                if forced[n // 2:i] != target[n // 2:i]:
                    continue
                return forced
        
        return ""







