class Solution:
    def maxDepthAfterSplit(self, seq: str) -> list[int]:
        a = []
        b = []
        aOpen = 0
        bOpen = 0
        for i, v in enumerate(seq):
            if v == '(':
                if aOpen <= bOpen:
                    aOpen += 1
                    a.append(i)
                else:
                    bOpen += 1
                    b.append(i)
            else:
                if aOpen >= bOpen:
                    aOpen -= 1
                    a.append(i)
                else:
                    bOpen -= 1
                    b.append(i)
        res = [None] * len(seq)
        for i in a:
            res[i] = 0
        for i in b:
            res[i] = 1
        return res