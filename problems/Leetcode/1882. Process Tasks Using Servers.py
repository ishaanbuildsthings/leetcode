class Solution:
    def assignTasks(self, servers: List[int], tasks: List[int]) -> List[int]:
        avail = SortedList((x, i) for i, x in enumerate(servers)) # available servers by weight, index
        release = SortedList() # will hold (time, server weight, index)
        res = [-1] * len(tasks)
        time = 0
        for j in range(len(tasks)):
            time = max(time, j)
            tsk = tasks[j]
            while release and release[0][0] <= time:
                rtime, rweight, rindex = release.pop(0)
                avail.add((rweight, rindex))
            if not avail:
                rtime, rweight, rindex = release.pop(0)
                time = rtime
                avail.add((rweight, rindex))
            earlyW, earlyI = avail.pop(0)
            res[j] = earlyI
            release.add((time + tsk, earlyW, earlyI))
        
        return res
