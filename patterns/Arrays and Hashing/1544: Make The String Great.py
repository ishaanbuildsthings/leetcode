# Difficulty: easy

# Solution, O(n) time and space, can use string building in a low level language for O(1) space

class Solution:
    def makeGood(self, s: str) -> str:

        def isConflict(c1, c2):
            if not c1: return False
            if c1.upper() == c2 and c1 != c2:
                return True
            if c1.lower() == c2 and c1 != c2:
                return True
            return False

        stack = []
        i = 0
        while i < len(s):
            if not stack:
                stack.append(s[i])
            elif isConflict(stack[-1], s[i]):
                stack.pop()
            else:
                stack.append(s[i])
            i += 1

        return ''.join(stack)

