class Solution:
    def numberOfDays(self, year: int, month: int) -> int:
        mToDays = {
            1 : 31,
            2 : 28,
            3 : 31,
            4:  30,
            5 : 31,
            6 : 30,
            7 : 31,
            8 : 31,
            9 : 30,
            10 : 31,
            11 : 30,
            12 : 31
        }
        if month != 2:
            return mToDays[month]
        # normal year
        if year % 4:
            return mToDays[month]
        if not year % 400:
            return 29
        if not year % 100:
            return 28
        return 29
        