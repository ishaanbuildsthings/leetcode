class Solution:
    def evaluateExpression(self, expression: str) -> int:
        # maps an index to its next ( in a >= position
        idxToOpen = {}
        earlyOpen = inf
        for i in range(len(expression) - 1, -1, -1):
            if expression[i] == '(':
                earlyOpen = i
            idxToOpen[i] = earlyOpen
        
        openToComma = {} # maps an ( position to its corresponding ,
        stack = []
        for i, v in enumerate(expression):
            if v == '(':
                stack.append(i)
                continue
            if v == ')':
                stack.pop()
                continue
            if v == ',':
                openToComma[stack[-1]] = i

        opMap = {
            'add' : lambda x, y : x + y,
            'sub' : lambda x, y : x - y,
            'mul' : lambda x, y : x * y,
            'div' : lambda x, y : x // y
        }

        def solve(l, r):
            open = idxToOpen[l]
            # no opening = just a plain int
            if open > r:
                return int(expression[l:r+1])
            comma = openToComma[open]
            L1 = open + 1
            R1 = comma - 1
            L2 = comma + 1
            R2 = r - 1

            lh = solve(L1, R1)
            rh = solve(L2, R2)

            string = expression[l:l+3]
            
            return opMap[string](lh, rh)
        
        return solve(0, len(expression) - 1)
            
