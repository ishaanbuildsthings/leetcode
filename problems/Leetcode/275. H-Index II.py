class Solution:
    def hIndex(self, citations: List[int]) -> int:
        
        def havePublishedHWithHCitations(h):
            hthSmallest = citations[-h]
            return hthSmallest >= h
            
        l = 0
        r = len(citations)
        while l <= r:
            m = (r + l) // 2
            if havePublishedHWithHCitations(m):
                l = m + 1
            else:
                r = m - 1

        return r