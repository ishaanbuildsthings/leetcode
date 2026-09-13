# palSet = set()
palList = []

odds = []
evens = []

def compute():
    for half in range(1, 10**5 + 1):
        full = str(half) + str(half)[::-1]
        palList.append(int(full))
        # palSet.add(int(full))
        # print(f'full is: {full}')
        for middle in range(10):
            nfull = str(half) + str(middle) + str(half)[::-1]
            # palSet.add(int(nfull))
            palList.append(int(nfull))
    # palList = sorted(palSet)
    # print(f'done: length is: {len(palList)}')

    for v in range(1, 10):
        palList.append(v)

    palList.sort()

    for v in palList:
        if v % 2:
            odds.append(v)
        else:
            evens.append(v)

def firstIndexGTE(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index if index < len(arr) else len(arr)

    
class Solution:
    def minOperations(self, nums: list[int]) -> int:

        if not palList:
            compute()

        # print(f'length is: {len(palList)}')
        # print(palList[:100])
        # print(f'pal set size isL {len(palSet)}')

        # print(len(palList) == len(set(palList)))

        # 99999 99999

        res = 0
        for i, v in enumerate(nums):
            # find leftmost >= this number
            bucket = odds if v % 2 else evens

            # print(f'bucket: {bucket}')

            # print(f'v is: {v}')

            leftmostI = firstIndexGTE(bucket, v)

            # print(f'leftmost i is: {leftmostI}')

            num = bucket[leftmostI]

            diff = abs(num - v)
            ops = diff // 2

            if leftmostI > 0:
                onLeft = bucket[leftmostI - 1]
                diff = abs(onLeft - v)
                ops = min(ops, diff // 2)

            res += ops

        return res
            

        
        