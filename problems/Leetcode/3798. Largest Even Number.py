class Solution:
    def largestEven(self, s: str) -> str:
        l = list(s)
        while l and l[-1] == '1':
            l.pop()
        return ''.join(l)