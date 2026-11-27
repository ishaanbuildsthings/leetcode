class Solution:
    def triangleNumber(self, nums: List[int]) -> int:
        c = Counter(nums)

        @cache
        def lt(side):
            if side == -1:
                return 0
            return c[side] + lt(side - 1)
        
        def query(l, r):
            return lt(r) - lt(l - 1)
        
        allVals = sorted(set(nums))
        if allVals[0] == 0:
            allVals.pop(0)

        res = 0
        for size1 in (allVals):
            for size2 in (allVals):
                if size2 < size1:
                    continue
                # size1 + size2 + (size2+1...size1+size2-1)
                neededBetween = query(size2+1,size1+size2-1)
                oldres = res
                if size1 != size2:
                    bottom2 = c[size1] * c[size2]
                else:
                    n = c[size1]
                    bottom2 = n * (n - 1) // 2
                
                res += max(0, bottom2 * neededBetween)

                # take the same as size2
                if size1 == size2:
                    n = c[size1]
                    # all three same
                    allSame = n * (n - 1) * (n - 2) // 6
                    res += max(0, allSame)
                else:
                    # top two are the same
                    n = c[size2]
                    top2Same = n * (n - 1) // 2
                    res += max(0, top2Same * c[size1])
                    
        
        return res
                
                

            