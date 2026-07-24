class Solution:
    def hardestWorker(self, n: int, logs: List[List[int]]) -> int:
        longestTime = logs[0][1]
        resId = logs[0][0]
        for i in range(1, len(logs)):
            idx, leaveTime = logs[i]
            pidx, pleaveTime = logs[i - 1]
            diffTime = leaveTime - pleaveTime
            if diffTime > longestTime:
                longestTime = diffTime
                resId = idx
            elif diffTime == longestTime:
                resId = min(resId, idx)
        return resId
