class Solution:
    def trap(self, h: List[int]) -> int:
        l=res=0
        r=len(h)-1
        lMax,rMax=h[0],h[-1]
        while l<=r:
            if lMax<=rMax:
                res+=lMax-h[l]
                l+=1
                if l < len(h):
                    lMax=max(lMax,h[l])
            else:
                res+=rMax-h[r]
                r-=1
                if r >= 0:
                    rMax=max(rMax,h[r])
        return res