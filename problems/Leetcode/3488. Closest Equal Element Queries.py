class Solution:
    def solveQueries(self, nums: List[int], queries: List[int]) -> List[int]:
        p = defaultdict(list)
        iToBucketAndIndex = {}
        indexToPosInBucket = {}
        for i, val in enumerate(nums):
            p[val].append(i)
            iToBucketAndIndex[(val, len(p[val]))] = i
            indexToPosInBucket[i] = len(p[val]) - 1
        # print(p)
        # print(iToBucketAndIndex)
        
        # print(f'index to pos in bucket: {indexToPosInBucket}')
                        
        res = []
        for index in queries:
            # print(f'index={index}')
            num = nums[index]
            bucket = p[num]
            posInBucket = indexToPosInBucket[index]
            neis = [] # index neighbors
            belowPosInBucket = (posInBucket - 1) % len(bucket) # can be above if wrapping around
            if belowPosInBucket != posInBucket:
                neis.append(bucket[belowPosInBucket])
            abovePosInBucket = (posInBucket+1) % len(bucket)
            if abovePosInBucket != posInBucket:
                neis.append(bucket[abovePosInBucket])
                
            def getMinDist(smallI, bigI):
                opt1 = bigI - smallI
                opt2 = smallI + (len(nums) - bigI)
                return min(opt1, opt2)
            
            minDist = inf
            for nei in neis:
                tiny = min(nei, index)
                big = max(nei, index)
                minDist = min(minDist, getMinDist(tiny, big))
            
            res.append(minDist if minDist != inf else -1)
        return res
                
    
            
            