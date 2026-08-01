class Solution:
    def reformatDate(self, date: str) -> str:
        date, month, year = date.split(' ')
        date = date[:2] if date[1].isdigit() else '0' + date[:1]
        mToWritten = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        idx = mToWritten.index(month)
        idx += 1
        if idx < 10:
            idx = '0' + str(idx)
        else:
            idx = str(idx)

        return year + '-' + idx + '-' + date