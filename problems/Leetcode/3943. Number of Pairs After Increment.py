# Wrong Answer
# 32 / 999 testcases passed
# Input
# nums1 =
# [7,2,7]
# nums2 =
# [1,3,9,1,2]
# queries =
# [[2,9]]
# Use Testcase
# Output
# [0]
# Expected
# [2]





# Wrong Answer
# 735 / 999 testcases passed
# Input
# nums1 =
# [8,4,5,2]
# nums2 =
# [1,8,5,4,6]
# queries =
# [[1,1,2,44],[2,8]]
# Use Testcase
# Output
# [1]
# Expected
# [2]



class Solution:
    def numberOfPairs(self, nums1: List[int], nums2: List[int], queries: List[List[int]]) -> List[int]:
        n = len(nums2)
        B = math.isqrt(n)
        numBuckets = n // B
        size = B * numBuckets
        extraBucket = False
        if size < n:
            numBuckets += 1
            extraBucket = True
            
        buckets = [] # holds (l, r)

        maps = [None] * numBuckets
        bucketGains = [0] * numBuckets

        idxToBucketId = [None] * n

        for i in range(numBuckets):
            l = i * B
            r = l + B - 1
            r = min(r, n - 1)
            buckets.append((l, r))

            mp = defaultdict(int)
            for j in range(l, r + 1):
                v = nums2[j]
                mp[v] += 1
                idxToBucketId[j] = i

            maps[i] = mp

        res = []

        for q in queries:
            if len(q) == 2:
                tot = q[-1]
                resHere = 0
                for bucketI in range(numBuckets):
                    bucketGain = bucketGains[bucketI]
                    mp = maps[bucketI]
                    for v1 in nums1:
                        req = tot - v1
                        find = mp[req - bucketGain]
                        resHere += find
                        
                res.append(resHere)
            else:
                _, l, r, gain = q

                leftB = idxToBucketId[l]
                L = l
                R = buckets[leftB][-1]
                R = min(R, r)
                mapLeft = maps[leftB]
                for j in range(L, R + 1):
                    oldV = nums2[j]
                    mapLeft[oldV] -= 1
                    newV = oldV + gain
                    mapLeft[newV] += 1
                    nums2[j] = newV

                rightB = idxToBucketId[r]
                if rightB != leftB:
                    L = buckets[rightB][0]
                    R = buckets[rightB][1]
                    R = min(R, r)
                    mapRight = maps[rightB]
                    for j in range(L, R + 1):
                        oldV = nums2[j]
                        mapRight[oldV] -= 1
                        newV = oldV + gain
                        mapRight[newV] += 1
                        nums2[j] = newV

                bL = leftB + 1
                bR = rightB - 1
                for bi in range(bL, bR + 1):
                    bucketGains[bi] += gain

        return res

            
        