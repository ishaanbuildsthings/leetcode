class Solution:
    def minRemoveToMakeValid(self, s: str) -> str:
        opens = 0
        stack = []
        for char in s:
            if char not in '()':
                stack.append(char)
                continue
            if char == '(':
                opens += 1
                stack.append(char)
                continue
            if not opens:
                continue
            opens -= 1
            stack.append(')')
        res = []
        for i in range(len(stack) - 1, -1, -1):
            if stack[i] != '(':
                res.append(stack[i])
                continue
            if opens:
                opens -= 1
                continue
            res.append('(')
        return ''.join(res[::-1])