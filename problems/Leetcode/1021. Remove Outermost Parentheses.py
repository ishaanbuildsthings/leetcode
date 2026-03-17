class Solution:
    def removeOuterParentheses(self, s: str) -> str:
        removeIndices = set()

        # could just use a counter of ( surplus i think
        stack = [] # holds (type, index)
        
        for i, c in enumerate(s):
            if c == '(':
                stack.append((c, i))
            if c == ')':
                if len(stack) == 1:
                    removeIndices.add(stack.pop()[1])
                    removeIndices.add(i)
                else:
                    stack.pop()
        
        return ''.join(
            s[i] for i in range(len(s)) if i not in removeIndices
        )