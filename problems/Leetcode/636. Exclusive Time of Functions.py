class Solution:
    def exclusiveTime(self, n: int, logs: List[str]) -> List[int]:
        times = [] # holds (time, idx, startOrEnd)
        for log in logs:
            idx, startOrEnd, time = log.split(':')
            idx = int(idx)
            time = int(time)
            times.append((time, idx, startOrEnd))
        res = [0] * n
        stack = []
        lastTime = 0
        for time, idx, startOrEnd in times:
            if not stack:
                stack.append(idx)
                lastTime = time
                continue
            if startOrEnd == 'start':
                prevIdx = stack[-1]
                gain = time - lastTime
                res[prevIdx] += gain
                stack.append(idx)
                lastTime = time
                continue
            gain = time - lastTime + 1
            res[idx] += gain
            stack.pop()
            lastTime = time + 1
        
        return res
        
        


