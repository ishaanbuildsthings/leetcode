class Solution:
    def findMismatchedSegments(self, s1: str, s2: str) -> list[list[str]]:
        res = []
        piece1 = []
        piece2 = []
        for i in range(len(s1)):
            v1 = s1[i]
            v2 = s2[i]
            if v1 != v2:
                piece1.append(v1)
                piece2.append(v2)
            else:
                if piece1:
                    res.append([
                        ''.join(piece1),
                        ''.join(piece2)
                    ])
                    piece1 = []
                    piece2 = []
        if piece1:
            res.append([
                ''.join(piece1),
                ''.join(piece2)
            ])
        return res
