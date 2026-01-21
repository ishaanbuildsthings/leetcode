class Solution:
    def goodIndices(self, s: str) -> List[int]:
        res = []
        n = len(s)
        for i in range(n):
            desired = str(i)
            length = len(desired)
            left = i - length + 1
            if left >= 0:
                if s[left:i+1] == desired:
                    res.append(i)
        return res