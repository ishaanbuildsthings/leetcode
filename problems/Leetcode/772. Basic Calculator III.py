
def calcNoParentheses(s):
    s = ''.join([x for x in s if x != ' '])
    symbols = [] # holds a number or an operator
    term = ''
    for i, v in enumerate(s):
        if v in '+-/*' and term != '':
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
        term = prev * nxt if v == '*' else int(prev / nxt)
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


class Solution:
    def calculate(self, s: str) -> int:
        lToR = {} # maps a left index ( to its right index )
        nestingDepths = defaultdict(list) # maps a nesting depth to a list of left indices
        stack = []
        open = 0
        for i, v in enumerate(s):
            if v not in '()':
                continue
            if v == '(':
                stack.append(i)
                open += 1
                continue
            popped = stack.pop()
            lToR[popped] = i
            open -= 1
            nestingDepths[open + 1].append(popped)

        sl = SortedList(range(len(s)))
        mxDepth = max(nestingDepths.keys(), default=0)

        vals = list(s) # current mapping of alive index -> present value

        while mxDepth:
            if not nestingDepths[mxDepth]:
                mxDepth -= 1
                continue
            bucket = nestingDepths[mxDepth] # all the lefts we need to process
            for left in bucket:
                right = lToR[left]
                l = sl.bisect_left(left)
                r = sl.bisect_left(right) # in the sl we go from l...r
                arr = []
                for i in range(l + 1, r):
                    idx = sl[i]
                    arr.append(vals[idx])
                string = ''.join(arr)
                aliveI = sl[l]
                evaluated = calcNoParentheses(string)
                vals[aliveI] = str(evaluated)
                for _ in range(l, r + 1):
                    sl.pop(l)
                sl.add(aliveI)
            nestingDepths[mxDepth] = []
        
        arr = []
        for i in sl:
            arr.append(vals[i])
        s = ''.join(arr)
        return calcNoParentheses(s)
                


            