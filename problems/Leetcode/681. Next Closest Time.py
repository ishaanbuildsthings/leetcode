class Solution:
    def nextClosestTime(self, time: str) -> str:
        def mp(timeString):
            h, m = timeString.split(':')
            return (int(h) * 60) + int(m)
        
        digits = set()
        for i in range(5):
            if i == 2:
                continue
            digits.add(int(time[i]))
                
        initTime = mp(time)
        res = None
        resTime = inf
        
        for d1 in digits:
            if d1 > 2:
                continue
            for d2 in digits:
                if d1 == 2:
                    if d2 >= 4:
                        continue
                for d3 in digits:
                    if d3 > 5:
                        continue
                    for d4 in digits:
                        timeS = str(d1) + str(d2) + ':' + str(d3) + str(d4)
                        timeNum = mp(timeS)
                        if timeNum > initTime and timeNum < resTime:
                            resTime = timeNum
                            res = timeS
                        elif timeNum <= initTime:
                            timeNum += (24 * 60)
                            if timeNum < resTime:
                                resTime = timeNum
                                res = timeS
        
        return res
            