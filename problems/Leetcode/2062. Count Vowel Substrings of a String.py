class Solution:
    def countVowelSubstrings(self, word: str) -> int:
        pieces = []
        piece = []
        for v in word:
            if v not in 'aeiou':
                if piece:
                    pieces.append(''.join(piece))
                    piece = []
            else:
                piece.append(v)
        if piece:
            pieces.append(''.join(piece))
        
        def process(piece):
            resHere = 0
            n = len(piece)
            l = r = 0
            c = Counter()
            while r < n:
                v = piece[r]
                c[v] += 1
                while len(c) == 5:
                    suffixes = n - r
                    resHere += suffixes
                    lost = piece[l]
                    c[lost] -= 1
                    if not c[lost]:
                        del c[lost]
                    l += 1
                r += 1
            return resHere
        
        return sum(process(x) for x in pieces)



