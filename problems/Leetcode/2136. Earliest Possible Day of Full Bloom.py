class Solution:
    def earliestFullBloom(self, plantTime: List[int], growTime: List[int]) -> int:
        def cmp(a, b):
            # if we plant a first
            aTime = a[0] + a[1]
            bTime = a[0] + b[0] + b[1]
            totAFirst = max(aTime, bTime)

            # plant b first
            bTime = b[0] + b[1]
            aTime = b[0] + a[0] + a[1]
            totBFirst = max(bTime, aTime)

            if totAFirst <= totBFirst:
                return -1
            
            return 1
        
        zipped = [[plantTime[i], growTime[i]] for i in range(len(plantTime))]
        zipped.sort(key=cmp_to_key(cmp))
        res = 0 # stores max
        time = 0 # curr time
        for plant, grow in zipped:
            finish = time + plant + grow
            res = max(res, finish)
            time += plant
        
        return res
