class Solution:
    def movesToStamp(self, stamp: str, target: str) -> List[int]:
        # SOLUTION 2, LESS CURSED O(n^3 / 64)
        S = len(stamp)
        T = len(target)
        mismatches = [] # for each left stamp edge, get a bitset of the mismatched positions
        for l in range(T):
            r = l + S - 1
            if r >= T:
                break
            # stamp from l...r
            bs = 0
            for pos in range(l, r + 1):
                if stamp[pos-l] != target[pos]:
                    bs |= (1 << (pos - l))
            mismatches.append(bs)
        
        stars = 0 # global bitset
        res = []

        while True:
            if stars.bit_count() == len(target):
                break
            resI = -1
            window = (1 << len(stamp)) - 1
            l = 0
            r = l + len(stamp) - 1
            while r < len(target):
                # mismatches in range are thing that are NOT a star AND are in mismatch
                bad = window & (~stars) & (mismatches[l] << l)
                numStars = (stars & window).bit_count()
                if not bad and numStars < len(stamp):
                    resI = l
                    break
                r += 1
                l += 1
                window <<= 1
            if resI == -1:
                return []
            res.append(resI)
            for pos in range(resI, resI + len(stamp)):
                stars |= (1 << pos)
        
        res.reverse()
        return res





        # SOLUTION 1, CURSED O(n^3 * 26 / 64)
        # n = len(target)
        # m = len(stamp)

        # current = list(target) # letters mean we need to match it, * means it was matched in the future
        # moves = []

        # sLetters = set()
        # for v in stamp:
        #     sLetters.add(v)

        # tLetters = set()
        # for v in target:
        #     tLetters.add(v)
        
        # if sLetters != tLetters:
        #     return []

        # while True:
        #     if all(ch == '*' for ch in current):
        #         break

        #     letterToMaskTarget = defaultdict(int)
        #     for i, v in enumerate(current):
        #         if v == '*':
        #             continue
        #         letterToMaskTarget[v] |= (1 << i)
            
        #     letterToMaskStamp = defaultdict(int)
        #     for i, v in enumerate(stamp):
        #         letterToMaskStamp[v] |= (1 << i)
            
        #     pf = []
        #     curr = 0
        #     for v in current:
        #         if v == '*':
        #             curr += 1
        #         pf.append(curr)
            
        #     def queryStar(l, r):
        #         return pf[r] - (pf[l - 1] if l else 0)
            
        #     placedI = -1
            
        #     for l in range(len(current)):
        #         r = l + len(stamp) - 1
        #         if r >= len(target):
        #             break
                
        #         # stamp from l...r
        #         starCount = queryStar(l, r)

        #         matchedLetters = 0
        #         for letter in sLetters:
        #             matchedLetters |= (letterToMaskStamp[letter] & letterToMaskTarget[letter])
                
        #         cnt = matchedLetters.bit_count()

        #         if cnt + starCount == len(stamp) and cnt > 0:
        #             placedI = l
        #             break
                
        #         for letter in sLetters:
        #             letterToMaskStamp[letter] <<= 1
            
        #     if placedI == -1:
        #         return []
            
        #     moves.append(placedI)
        #     for i in range(placedI, placedI + len(stamp)):
        #         current[i] = '*'

            

        # moves.reverse()
        # return moves