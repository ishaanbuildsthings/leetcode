class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        for i in range(len(intervals)):
            ival = intervals[i]
            start, end = ival
            if start >= newInterval[0]:
                intervals.insert(i, newInterval)
                break
        if not intervals:
            intervals = [newInterval]
        if intervals[-1][0] < newInterval[0]:
            intervals.append(newInterval)
        
        res = []
        # merge intervals
        currStart, currEnd = intervals[0]
        for i in range(1, len(intervals)):
            start, end = intervals[i]
            if currEnd >= start:
                currEnd = max(currEnd, end)
            else:
                res.append([currStart, currEnd])
                currStart, currEnd = start, end
        res.append([currStart, currEnd])
        return res