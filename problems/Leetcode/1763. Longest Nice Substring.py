class Solution:
    def longestNiceSubstring(self, s: str) -> str:
        
        # track up to 52 masks ending at r, specifically their leftmost positions
        # when we transition to the next r+1, we loop over the at most 52 previous masks and create up to 52 new ones ending at r+1, we take the leftmost position too
        resSize = 0
        resL = -1
        resR = -1
        leftmosts = {} # maps (maskLower, maskUpper) -> leftmost index
        for r, v in enumerate(s):
            nleft = {}
            low = 0 if v.isupper() else 1 << (ord(v) - ord('a'))
            high = 0 if v.islower() else 1 << (ord(v) - ord('A'))
            nleft[low, high] = r

            for (oldLow, oldHigh), leftmostIdx in leftmosts.items():
                nlow = low | oldLow
                nhigh = high | oldHigh
                nleft[nlow, nhigh] = leftmostIdx
                width = r - leftmostIdx + 1
                if nlow == nhigh and width > resSize:
                    resSize = width
                    resL = leftmostIdx
                    resR = r
            
            leftmosts = nleft
        return s[resL:resR+1] if resSize else ''
            
                