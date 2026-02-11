class Solution:
    def delayedCount(self, nums: List[int], k: int) -> List[int]:
        n = len(nums)
        res = [None] * n

        def solveBucket(bucket):
            j = 0
            for i in range(len(bucket)):
                idx = bucket[i]
                lowest = idx + k + 1
                if j >= len(bucket):
                    res[idx] = 0
                    continue
                while j < len(bucket) and bucket[j] < lowest:
                    j += 1
                remain = len(bucket) - j
                res[idx] = remain
                
        
        numToIdxs = defaultdict(list)
        for i, v in enumerate(nums):
            numToIdxs[v].append(i)

        for key, bucket in numToIdxs.items():
            print(f'{bucket}')
            solveBucket(bucket)

        return res

