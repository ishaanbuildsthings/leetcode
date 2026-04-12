class Solution:
    def minBuildTime(self, blocks: List[int], split: int) -> int:
        
        blocks.sort()
        l=0
        r= 10**12 # just an estinate
        res=None
        def do(t):
            times = blocks[:]
            cur=1
            time=0
            while times:
                if cur>=len(times) and time + times[-1] <= t: return True
                while (times and times[-1] + time + split > t):
                    cur-=1
                    lst=times.pop()
                    if cur<0 or (cur==0 and times): return False
                    if time+lst>t: return False
                cur*=2
                time+=split
            return True
        while l<=r:
            m=(r+l)//2
            if do(m):
                res=m
                r=m-1
            else:
                l=m+1
        return res