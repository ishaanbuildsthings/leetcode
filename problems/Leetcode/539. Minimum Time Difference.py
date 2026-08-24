from functools import cmp_to_key

class Solution:
    def findMinDifference(self, timePoints: List[str]) -> int:
        def timeComparator(time1, time2):
            time1Hour = int(time1[:2])
            time2Hour = int(time2[:2])
            time1Minutes = int(time1[3:])
            time2Minutes = int(time2[3:])
            if time1Hour < time2Hour:
                return -1
            if time1Hour > time2Hour:
                return 1
            return -1 if time1Minutes < time2Minutes else 1 if time1Minutes > time2Minutes else 0

        sortedTimes = sorted(timePoints, key=cmp_to_key(timeComparator))

        def timeDiffInMinutes(earlierTime, laterTime):
            minuteDifference = int(laterTime[3:]) - int(earlierTime[3:])
            hourDifference = int(laterTime[:2]) - int(earlierTime[:2])
            totalMinuteDifference = hourDifference * 60 + minuteDifference
            return totalMinuteDifference


        return min(
            min(timeDiffInMinutes(sortedTimes[i], sortedTimes[i + 1]) for i in range(len(sortedTimes) - 1)),
            timeDiffInMinutes(sortedTimes[-1], str(24 + int(sortedTimes[0][:2])) + sortedTimes[0][2:])
        )
