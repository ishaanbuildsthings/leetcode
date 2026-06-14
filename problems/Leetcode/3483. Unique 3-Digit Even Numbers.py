class Solution:
    def totalNumbers(self, digits: List[int]) -> int:
        res = 0
        digits = [str(digit) for digit in digits]
        c = Counter(digits)
        # print(c)
        for number in range(100, 1000):
            if number % 2:
                continue
            c2 = Counter(str(number))
            # print(c2)
            foundFail = False
            for key in c2:
                if c[key] < c2[key]:
                    foundFail = True
            if not foundFail:
                res += 1
        return res
                    