class Solution:
    def evaluate(self, s: str, knowledge: List[List[str]]) -> str:
        mp = {a : b for a, b in knowledge}
        res = []
        piece = []
        for v in s:
            if v == '(':
                if piece:
                    val = ''.join(piece)
                    res.append(val)
                    piece = []
                continue
            if v != ')':
                piece.append(v)
                continue
            val = ''.join(piece)
            res.append(mp.get(val, '?'))
            piece = []
        if piece:
            res.append(''.join(piece))
        return ''.join(res)