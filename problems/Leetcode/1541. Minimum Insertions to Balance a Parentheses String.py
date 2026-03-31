class Solution:
    def minInsertions(self, s: str) -> int:
        res = 0
        stack = []
        for v in s:
            if v == '(':
                if not stack or stack[-1] == '(':
                    stack.append('(')
                    continue
                res += 1
                stack.pop()
                stack.pop()
                stack.append('(')
                continue
            if not stack:
                stack.append('(')
                res += 1
                stack.append(')')
                continue
            if stack[-1] == '(':
                stack.append(')')
                continue
            stack.pop()
            stack.pop()
        while stack:
            if stack[-1] == ')':
                res += 1
                stack.pop()
                stack.pop()
            else:
                res += 2
                stack.pop()
        return res