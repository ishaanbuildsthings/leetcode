class Solution:
    def canEat(self, candiesCount: List[int], queries: List[List[int]]) -> List[bool]:
        n = len(candiesCount)
        pf = []
        curr = 0
        for v in candiesCount:
            curr += v
            pf.append(curr)
        
        def query(l, r):
            if l>r: return 0
            return pf[r] - (pf[l-1] if l else 0)
        
        res = []
        for favType, favDay, cap in queries:
            # we need the leftmost candy type that can be eaten
            # so if we only ate favDay candies, whats the leftmost candy type we can do that on?
            l = 0
            r = n - 1
            leftmost = None
            while l<=r:
                m = (r+l)//2
                tot = query(0, m)
                if tot > favDay: # exclusive! since we start on day 0
                    leftmost = m
                    r = m - 1
                else:
                    l = m + 1
            
            # and the rightmost
            l = 0
            r = n - 1
            rightmost = None
            while l <= r:
                m = (r+l)//2
                totBefore = query(0, m-1)
                totalCandiesEaten = totBefore + 1
                days = math.ceil(totalCandiesEaten / cap) 
                if days <= favDay + 1: # convert to 0 indexing
                    rightmost = m
                    l = m + 1
                else:
                    r = m - 1
            
            if leftmost is None or rightmost is None: # could happen if theres more candies than days
                res.append(False)
                continue
            
            res.append(leftmost <= favType <= rightmost)
        
        return res