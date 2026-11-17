class Solution:
    def clumsy(self, n: int) -> int:
        go = {
            '*' : '/',
            '/' : '+',
            '+' : '-',
            '-' : '*'
        }

        arr = []
        op = '*'
        for num in range(n, 0, -1):
            arr.append(num)
            if num != 1:
                arr.append(op)
                op = go[op]
        
        # compute products
        stack = []
        for i, v in enumerate(arr):
            if str(v) in '*+-/':
                stack.append(v)
                continue
            if not stack:
                stack.append(v)
                continue
            prevOp = stack[-1]
            if prevOp in '+-':
                stack.append(v)
                continue
            op = stack.pop()
            num = stack.pop()
            if op == '*':
                stack.append(num * v)
            else:
                stack.append(num // v)
        
        res = 0
        for i in range(0, len(stack), 2):
            if i == 0 or stack[i - 1] == '+':
                res += stack[i]
            else:
                res -= stack[i]
        
        return res