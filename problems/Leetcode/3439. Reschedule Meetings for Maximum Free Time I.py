class Solution:
    def maxFreeTime(self, eventTime: int, k: int, startTime: List[int], endTime: List[int]) -> int:
        es = []
        for i in range(len(startTime)):
            es.append([startTime[i],endTime[i]])
        # print(es)
        # tot = 0
        # for a, b in es:
        #     tot += (b-a)
        # return eventTime-tot
        
        l = 0
        r = k - 1
        res = 0
        curr = 0
        
        # when we reschedule k, we take the previous end time to the next start time, minus curr size
        for i in range(k):
            curr += (es[i][1]-es[i][0])
            
        while r < len(es):
            if l > 0:
                prevEnd = es[l-1][1]
            else:
                prevEnd = 0
            
            if r == len(startTime) - 1:
                nextStart = eventTime
            else:
                nextStart = es[r+1][0]
            
            totalSpace = nextStart-prevEnd
            compressed = totalSpace - curr
            res = max(res, compressed)
            
            if r == len(es) - 1:
                break
            
            r += 1
            gained = es[r]
            curr += (gained[1]-gained[0])
            lost = es[l]
            curr -= (lost[1]-lost[0])
            l += 1
        
        return res
                    
            
            