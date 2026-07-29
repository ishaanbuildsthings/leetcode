class Solution:
    def dayOfYear(self, date: str) -> int:
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        y, m, d = date.split('-')
        y = int(y)
        m = int(m)
        d = int(d)

        isLeap = False
        if y % 4 == 0:
            isLeap = True
            if y % 100 == 0:
                isLeap = False
                if y % 400 == 0:
                    isLeap = True
        
        if isLeap:
            days[1] += 1
        
        daysCount = 0
        for month in range(m - 1):
            daysCount += days[month]
        daysCount += d
        return daysCount