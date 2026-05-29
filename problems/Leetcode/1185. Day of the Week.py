class Solution:
    def dayOfTheWeek(self, day: int, month: int, year: int) -> str:
        
        def isLeapYear(yr):
            if yr % 4 == 0:
                if yr % 400 == 0:
                    return True
                if yr % 100 == 0:
                    return False
                return True
            return False
        
        months = [
            31,
            29 if isLeapYear(year) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31
        ]

        total = 0
        # days up to but not including the current year
        for yr in range(1971, year):
            total += 365 if not isLeapYear(yr) else 366
        
        for mt in range(month - 1):
            total += months[mt]
        
        total += day

        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        return days[(total + 4) % 7]