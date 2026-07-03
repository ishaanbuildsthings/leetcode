class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        for v in s:
            if v != 'c':
                stack.append(v)
                continue
            if len(stack) >= 2 and stack[-1] == 'b' and stack[0] == 'a':
                stack.pop(); stack.pop()
                continue
            return False
        return len(stack) == 0