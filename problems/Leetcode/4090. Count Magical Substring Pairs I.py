class Solution:
    def countMagicalPairs(self, inputS: str) -> int:

        def getLefts(s):
            n = len(s)
            masks = {}
            dp = []

            for i in range(n):
                v = s[i]
                bit = 1 << (ord(v) - ord('a'))
                nmasks = {}
                for oldMask, leftReach in masks.items():
                    nmask = oldMask | bit
                    if nmask not in nmasks:
                        nmasks[nmask] = leftReach
                    else:
                        nmasks[nmask] = min(nmasks[nmask], leftReach)
                if bit not in nmasks:
                    nmasks[bit] = i
                
                masks = nmasks
                dp.append(masks)
            
            counts = [] # counts[i][distinct] is the # of substrings ending at ...i with that many distinct chars
            for i in range(n):
                distinctToLeftReach = [None] * 27
                masks = dp[i]
                for mask, leftReach in masks.items():
                    sz = mask.bit_count()
                    distinctToLeftReach[sz] = leftReach

                prevLeftReach = i + 1
                distinctToSize = [None] * 27
                for distinct in range(1, 27):
                    if distinctToLeftReach[distinct] is None:
                        break
                    leftReach = distinctToLeftReach[distinct]
                    width = prevLeftReach - leftReach
                    distinctToSize[distinct] = width
                    prevLeftReach = leftReach

                counts.append(distinctToSize)
            
            return counts

        
        counts1 = getLefts(inputS)
        counts2 = getLefts(inputS[::-1])
        res = 0
        for i in range(len(inputS) - 1):
            for distinct in range(1, 27):
                leftOpts = counts1[i][distinct]
                if leftOpts is None:
                    break
                rightI = len(inputS) - i - 2
                rightOpts = counts2[rightI][distinct]
                if rightOpts is None:
                    break
                res += leftOpts * rightOpts
        return res



                
                

