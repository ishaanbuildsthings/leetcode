class Solution:
    def minEliminationTime(self, timeReq: List[int], splitTime: int) -> int:
        # solution 1
        # binary search on the min time we can finish
        # we basically split greedily but whenever we must kill a strain or we would time out, we do that
        # log search checks, and for a check we basically duplicate up to at most logn times
        # i think its log * n but could be improved to log^2 ? cause we don't need to actually enumerate all n strains maybe?
        # EDIT: claude said this, so not exactly my idea:
        # Yes, the checker can be O(log² n) instead of O(n). The idea: at each split step (there are at most log n of them), instead of popping strains one-by-one, you binary search on the sorted array to find how many strains are too large to survive another split.
        # so that would make it log^3 n

        
        timeReq.sort()
        l=0
        r= 10**12 # just an estinate
        res=None
        def do(t):
            times = timeReq[:]
            cur=1
            time=0
            while times:
                if cur>=len(times) and time + times[-1] <= t: return True
                while (times and times[-1] + time + splitTime > t):
                    cur-=1
                    lst=times.pop()
                    if cur<0 or (cur==0 and times): return False
                    if time+lst>t: return False
                cur*=2
                time+=splitTime
            return True
        while l<=r:
            m=(r+l)//2
            if do(m):
                res=m
                r=m-1
            else:
                l=m+1
        return res