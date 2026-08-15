class Solution:
    def mergeCharacters(self, s: str, k: int) -> str:
        uniq = set(s)
        stack = []
        rightmost = {}
        deleted = 0
        for i, v in enumerate(s):
            if v not in rightmost:
                rightmost[v] = i - deleted
                stack.append(v)
                continue
            realPos = i - deleted
            dist = realPos - rightmost[v]
            if dist > k:
                stack.append(v)
                rightmost[v] = realPos
                continue
            deleted += 1
        
        return ''.join(stack)