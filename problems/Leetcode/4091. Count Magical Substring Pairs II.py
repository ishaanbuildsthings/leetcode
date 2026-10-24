class Solution:
    def countMagicalPairs(self, inputS: str) -> int:

        def getLefts(s):
            n = len(s)
            masks = {}
            counts = [] # counts[i][distinct] is the # of substrings ending at i with that many distinct chars

            for i in range(n):
                v = s[i]
                bit = 1 << (ord(v) - ord('a'))
                nmasks = {}
                for oldMask, oldCount in masks.items():
                    nmask = oldMask | bit
                    if nmask not in nmasks:
                        nmasks[nmask] = oldCount
                    else:
                        nmasks[nmask] += oldCount
                nmasks[bit] = nmasks.get(bit, 0) + 1
                
                masks = nmasks

                distinctToCount = [None] * 27
                for mask, count in masks.items():
                    distinctToCount[mask.bit_count()] = count
                counts.append(distinctToCount)
            
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



                
                


