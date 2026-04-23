class Solution:
    def distance(self, arr: List[int]) -> List[int]:
        buckets = defaultdict(list) # maps num -> indices
        for i, val in enumerate(arr):
            buckets[val].append(i)
        valAndIndexToDistance = {} # maps (val, index) -> distance
        
        for valType in buckets:
            bucket = buckets[valType]
            currDistance = sum(bucket[i] - bucket[0] for i in range(1, len(bucket)))
            firstIndex = bucket[0]
            valAndIndexToDistance[(valType, firstIndex)] = currDistance
            for i in range(1, len(bucket)):
                index = bucket[i]
                elementsOnLeftThatMovedAway = i
                currDistance += elementsOnLeftThatMovedAway * (index - bucket[i - 1])
                elementsOnRightThatMovedCloser = len(bucket) - i
                currDistance -= elementsOnRightThatMovedCloser * (index - bucket[i - 1])
                valAndIndexToDistance[(valType, index)] = currDistance
        
        res = []
        for i in range(len(arr)):
            val = arr[i]
            res.append(valAndIndexToDistance[(val, i)])
        return res