class Solution:
    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
        intervals.sort()
        for i in range(len(intervals) - 1):
            ival = intervals[i]
            nextIval = intervals[i + 1]
            if ival[1] > nextIval[0]:
                return False
        return True