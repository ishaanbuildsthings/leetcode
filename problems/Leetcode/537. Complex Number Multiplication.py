class Solution:
    def complexNumberMultiply(self, num1: str, num2: str) -> str:
        one = num1.split('+')
        two = num2.split('+')

        real = int(one[0]) * int(two[0])
        last = int(one[1][:-1]) * int(two[1][:-1])
        real += -1 * last

        outer = int(one[0]) * int(two[1][:-1])
        inner = int(two[0]) * int(one[1][:-1])
        imaginary = inner + outer

        return f'{real}+{imaginary}i'

