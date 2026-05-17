class Solution:
    def solveEquation(self, equation: str) -> str:
        # get Xs and numbers on each side
        # put Xs on one side and numbers on the other

        L, R = equation.split('=')

        # gives us [Xs, number]
        def make(s):
            if s[0] != '-':
                s = '+' + s
            i = 0
            output = [0, 0]
            while i < len(s):
                number = []
                sign = 1 if s[i] == '+' else -1
                isXTerm = False
                for j in range(i + 1, len(s)):
                    d = s[j]
                    if d.isnumeric():
                        number.append(d)
                        continue
                    if d == 'x':
                        isXTerm = True
                        j += 1
                        break
                    # start of next term, we will set to this j
                    break
                number = int(''.join(number)) if number else 1
                gain = sign * number
                if isXTerm:
                    output[0] += gain
                else:
                    output[1] += gain
                i = j if j != len(s) - 1 else len(s)
            return output
        
        b1 = make(L)
        b2 = make(R)
        xsLeft = b1[0] - b2[0]
        numsRight = b2[1] - b1[1]
        if xsLeft == 0:
            if numsRight != 0:
                return 'No solution'
            return 'Infinite solutions'
        right = numsRight // xsLeft
        return f'x={right}'
        



