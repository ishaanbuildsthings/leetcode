class Solution:
    def getFactors(self, n: int) -> List[List[int]]:
        facs = []
        for potFac in range(2, n):
            if not n % potFac:
                facs.append(potFac)
        
        res = []
        def backtrack(bucket, i, remain):
            if remain == 1:
                if bucket:
                    res.append(bucket[:])
                return
            if i == len(facs):
                return
            # can always skip
            backtrack(bucket, i + 1, remain)

            # take current factor
            if not remain % facs[i]:
                bucket.append(facs[i])
                backtrack(bucket, i, remain // facs[i])
                bucket.pop()
        
        backtrack([], 0, n)
        return res
            
            