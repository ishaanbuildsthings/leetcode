class Solution:
    def thousandSeparator(self, n: int) -> str:
        rev = []
        s = str(n)
        for i in range(len(s) - 1, -1, -1):
            rev.append(s[i])
            if i != 0 and (len(s) - i) % 3 == 0:
                rev.append('.')
        return ''.join(rev)[::-1]