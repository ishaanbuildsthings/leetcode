class Solution:
    def findPattern(self, board: List[List[int]], pattern: List[str]) -> List[int]:
        h = len(board)
        w = len(board[0])
        h2 = len(pattern)
        w2 = len(pattern[0])
        for r in range(h - h2 + 1):
            for c in range(w - w2 + 1):
                mp = {} # number => letter
                mpRev = {} # letter => number, needed for bijection
                fail = False
                for rr in range(r, r + h2):
                    if fail:
                        break
                    for cc in range(c, c + w2):
                        v = board[rr][cc]
                        letter = pattern[rr - r][cc - c]
                        if not letter.isalpha():
                            if int(letter) != v:
                                fail = True
                                break
                            continue
                        if v in mp:
                            if mp[v] != letter:
                                fail = True
                                break
                        if letter in mpRev:
                            if mpRev[letter] != v:
                                fail = True
                                break
                        mp[v] = letter
                        mpRev[letter] = v
                if not fail:
                    return [r, c]
        return [-1, -1]