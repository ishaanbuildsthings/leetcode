class Solution:
    def longestBalanced(self, nums: List[int]) -> int:
        n = len(nums)
        B =  math.isqrt(n)
        numBlocks = n // B
        if n % B:
            numBlocks += 1

        # maps bi -> early cut dicts
        blockMaps = [{0:-1} for _ in range(numBlocks)]
        blockSums = [0] * numBlocks
        arr = [0] * n

        def refreshBlock(b):
            l = b * B
            r = min(n - 1, l + B - 1)
            earlyCut = {}
            earlyCut[0] = l - 1
            runningSum = 0
            for i in range(l, r + 1):
                v = arr[i]
                runningSum += v
                if runningSum not in earlyCut:
                    earlyCut[runningSum] = i
            blockMaps[b] = earlyCut
            blockSums[b] = runningSum
        
        # def pointUpdate(i, newV):
        #     arr[i] = newV
        #     block = i // B
        #     refreshBlock(block)

        rights = {} # global map of rightmost occurrence of each number

        # kind of like an append as we are increasing
        def add(v, i):
            if v % 2:
                arr[i] = 1
            else:
                arr[i] = -1

            if v in rights:
                oldI = rights[v]
                arr[oldI] = 0
                if oldI == i:
                    # refreshBlock(i // B)
                    rights[v] = i
                    return
                if oldI // B < i // B:
                    refreshBlock(oldI // B)
            rights[v] = i
            if i % B == B - 1:
                refreshBlock(i // B)
        
        res = 0

        # ending at i
        def query(i):
            resHere = 0
            br = i // B
            blockStart = br * B

            currTot = 0
            for r in range(i, blockStart - 1, -1):
                currTot += arr[r]
                if currTot == 0:
                    resHere = i - r + 1

            # within one block only
            if br == 0:
                return resHere
            
            for b in range(br - 1, -1, -1):
                blockSum = blockSums[b]
                blockMap = blockMaps[b]
                if currTot + blockSum in blockMap:
                    earlyI = blockMap[currTot + blockSum]
                    resHere = i - earlyI
                currTot += blockSum
            
            return resHere
        
        for i, v in enumerate(nums):
            add(v, i)
            res = max(res, query(i))
        
        return res
            

