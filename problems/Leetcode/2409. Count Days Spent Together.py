class Solution:
    def countDaysTogether(self, arriveAlice: str, leaveAlice: str, arriveBob: str, leaveBob: str) -> int:
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        def parse(dateStr):
            halves = dateStr.split('-')
            firstHalf = int(halves[0])
            completedDays = sum(days[i] for i in range(firstHalf - 1))
            secondDays = int(halves[-1])
            return completedDays + secondDays
        
        range1 = [parse(arriveAlice), parse(leaveAlice)]
        range2 = [parse(arriveBob), parse(leaveBob)]

        L = max(range1[0], range2[0])
        R = min(range1[1], range2[1])
        if R - L < 0:
            return 0
        return R - L + 1