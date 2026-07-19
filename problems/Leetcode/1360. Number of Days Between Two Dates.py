class Solution:
    def daysBetweenDates(self, date1: str, date2: str) -> int:

        def isLeapYear(yr):
            if yr % 4 != 0:
                return False
            # if it is divisible by 4, it is a leap, unless divisible by 100, unless unless divisible by 400
            if yr % 400 == 0:
                return True
            if yr % 100 == 0:
                return False
            return True
        
        
        # complete days from time 0
        def from0(date):
            y, m, d = map(int, date.split('-'))
            completeYears = y
            
            normalYears = 0
            leapYears = 0
            for yr in range(y):
                if isLeapYear(yr):
                    leapYears += 1
                else:
                    normalYears += 1
            
            normalDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            completeMonths = m - 1

            completedDaysFromYears = (365 * normalYears) + (366 * leapYears)

            completedDaysFromMonths = sum(normalDays[:completeMonths])

            completedDays = d

            completed = completedDaysFromYears + completedDaysFromMonths + completedDays

            # edge case, if current year is a leap year and we passed feb then we gain a day
            # don't need to handle if today is feb29, handled by day calculation
            if isLeapYear(y) and m > 2:
                completed += 1

            return completed
        
        a1 = from0(date1)
        a2 = from0(date2)
        return abs(a1 - a2)
            