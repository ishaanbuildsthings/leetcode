class Solution:
    def minMergeCost(self, lists: List[List[int]]) -> int:


        @cache
        def median(mask):
            lst = []
            for i in range(len(lists)):
                if (mask & (1 << i)):
                    lst.extend(lists[i])
            lst.sort()
            half = (len(lst) - 1) // 2
            return lst[half]
        
        @cache
        def length(mask):
            if mask.bit_count() == 0:
                return 0
            msb = mask.bit_length() - 1
            sz = len(lists[msb])
            return sz + length(mask ^ (1 << msb))

        @cache
        def minProduce(mask):
            if mask.bit_count() == 1:
                return 0
            submask = mask
            res = inf
            while submask:
                submask = (submask - 1) & mask
                if not submask:
                    break
                
                s2 = mask ^ submask

                m1 = median(submask)
                m2 = median(s2)

                len1 = length(submask)
                len2 = length(s2)

                ans = len1 + len2 + abs(m1 - m2) + minProduce(submask) + minProduce(s2)
                res = min(res, ans)
            return res
        
        fmask = (1 << len(lists)) - 1
        return minProduce(fmask)


        