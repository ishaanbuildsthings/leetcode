class Solution:
    def lexSmallestAfterDeletion(self, s: str) -> str:
        c = Counter(s)
        stack = []
        for v in s:
            while stack and stack[-1] > v and c[stack[-1]] > 1:
                c[stack.pop()] -= 1
            stack.append(v)
        while stack and c[stack[-1]] > 1:
            c[stack.pop()] -= 1
        
        return ''.join(stack)