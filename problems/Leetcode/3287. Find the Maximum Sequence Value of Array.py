class Solution:
    def maxValue(self, nums: List[int], k: int) -> int:
        # mlg dp
        # pref[i][seqTaken] is for the first i elements (so 0...i-1), we do this because otherwise pref[0] needs to look back
        # at a base case which makes the implementation very annoying, we want pref[0] to indicate the base case

        # suff[i][seqTaken] is different though, since we are looking on the right, suff[i] is for i..., and the base case is at suff[n], we can do this instead of pref[-1] because the array expands to the right as long as we want

        n = len(nums)
        pref = [[0 for _ in range(k + 1)] for _ in range(n + 1)]
        suff = [[0 for _ in range(k + 1)] for _ in range(n + 1)]
        for i in range(n + 1):
            pref[i][0] = 1
            suff[i][0] = 1

        def update(mask, value):
            nmask = 0
            for bit in range(2**7):
                if (1 << bit) & mask:
                    nmask |= 1 << (bit | value)
            return nmask
        
        for i in range(1, n + 1):
            for seqTaken in range(1, k + 1):
                skipMask = pref[i - 1][seqTaken]
                takeMask = update(pref[i - 1][seqTaken - 1], nums[i-1])
                pref[i][seqTaken] = skipMask | takeMask
        
        for i in range(n -1, -1, -1):
            for seqTaken in range(1, k + 1):
                skipMask = suff[i + 1][seqTaken]
                takeMask = update(suff[i+1][seqTaken-1],nums[i])
                suff[i][seqTaken] = skipMask | takeMask
        
        res = 0
        for i in range(n + 1):
            prefMask = pref[i][k]
            suffMask = suff[i][k]
            for bit1 in range(2**7):
                if not (1 << bit1) & prefMask:
                    continue
                for bit2 in range(2**7):
                    if not (1 << bit2) & suffMask:
                        continue
                    res = max(res, bit1 ^ bit2)
        
        return res
        



        # my jank dp
        # n = len(nums)
        # pref = [[0 for _ in range(k + 1)] for _ in range(n)] # pref[i][seqI] is a bitmask of doable values for 0...i when we have taken seqI+1 values
        # suff = [[0 for _ in range(k + 1)] for _ in range(n)]

        # for i in range(n):
        #     pref[i][0] = 1 # by default nothing is doable
        #     suff[i][0] = 1

        # for i in range(n):
        #     for seqI in range(k, 0, -1): # this did not need to be backwards since we always read from i-1
        #         if i == 0:
        #             prevSkipMask = 0
        #             prevMaskForTake = 1 if seqI == 1 else 0
        #         else:
        #             prevSkipMask = pref[i-1][seqI]
        #             prevMaskForTake = pref[i-1][seqI-1]
        #         nmaskIfTake = 0
        #         for prevBit in range(2**7):
        #             if prevMaskForTake & (1 << prevBit):
        #                 newOR = prevBit | nums[i]
        #                 nmaskIfTake |= (1 << newOR)
        #         pref[i][seqI] = nmaskIfTake | prevSkipMask
                
        # for i in range(n - 1, -1, -1):
        #     for seqI in range(k, 0, -1):
        #         if i == n - 1:
        #             nextSkipMask = 0
        #             nextMaskForTake = 1 if seqI == 1 else 0
        #         else:
        #             nextSkipMask = suff[i + 1][seqI]
        #             nextMaskForTake = suff[i + 1][seqI - 1]
        #         nmaskIfTake = 0
        #         for nextBit in range(2**7):
        #             if nextMaskForTake & (1 << nextBit):
        #                 newOR = nextBit | nums[i]
        #                 nmaskIfTake |= (1 << newOR)
        #         suff[i][seqI] = nmaskIfTake | nextSkipMask
        
        # res = 0
        # for i in range(n - 1):
        #     prefMask = pref[i][k]
        #     suffMask = suff[i+1][k]
        #     for bit1 in range(2**7):
        #         if not prefMask & (1 << bit1):
        #             continue
        #         for bit2 in range(2**7):
        #             if not suffMask & (1 << bit2):
        #                 continue
        #             res = max(res, bit1 ^ bit2)
        
        # return res

                