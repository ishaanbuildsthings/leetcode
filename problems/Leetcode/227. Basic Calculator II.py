class Solution:
    def calculate(self, s: str) -> int:
        s = ''.join([x for x in s if x != ' '])
        symbols = [] # holds a number or an operator
        term = ''
        for i, v in enumerate(s):
            if v in '+-/*':
                symbols.append(term)
                symbols.append(v)
                term = ''
            else:
                term += v
        symbols.append(term)

        stack = []
        i = 0
        while i < len(symbols):
            v = symbols[i]
            if not stack:
                stack.append(v)
                i += 1
                continue
            if v not in '/*':
                stack.append(v)
                i += 1
                continue
            prev = int(stack[-1])
            nxt = int(symbols[i + 1])
            stack.pop()
            term = prev * nxt if v == '*' else prev // nxt
            stack.append(str(term))
            i += 2
        res = int(stack[0])
        for i in range(2, len(stack), 2):
            prev = stack[i - 1]
            v = int(stack[i])
            if prev == '-':
                res -= v
            else:
                res += v
        return res