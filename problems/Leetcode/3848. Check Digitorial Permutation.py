class Solution:
    def isDigitorialPermutation(self, n: int) -> bool:
        @cache
        def numFac(num):
            if num == 1:
                return 1
            if num == 0:
                return 1
            return num * numFac(num - 1)

        tot = 0
        s = str(n)
        for i in range(len(s)):
            d = int(s[i])
            tot += numFac(d)

        s2 = str(tot)
        c = Counter(s2) # desired sum

        if c == Counter(str(s)):
            return True

        return False