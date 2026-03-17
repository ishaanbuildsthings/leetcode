class Solution:
    def removeDuplicates(self, s: str) -> str:
        stack = []
        for i, c in enumerate(s):
            if not stack or stack[-1] != c:
                stack.append(c)
                continue
            while stack and stack[-1] == c:
                stack.pop()
        return ''.join(stack)
