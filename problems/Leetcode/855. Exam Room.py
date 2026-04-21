class ExamRoom:
    def __init__(self, n: int):
        self.n = n
        self.bySize = SortedList() # holds (-score if placed at midpoint, l, r)
        # these all assume placing in the middle, for the edge ones we handle those separately in the seat function
        # if they tie by score it goes to l which breaks the next tie
        self.byPos = SortedList() # holds (l, r)
        self._add(0, n - 1)
    
    def _add(self, l, r):
        if l > r:
            return
        size = r - l + 1
        score = (size + 1) // 2
        self.bySize.add((-score, l, r))
        self.byPos.add((l, r))
    
    def _rem(self, l, r):
        if l > r:
            return
        size = r - l + 1
        score = (size + 1) // 2
        self.bySize.remove((-score, l, r))
        self.byPos.remove((l, r))
    
    # we identified the specific index, pos, to sit at, and the current interval it is in
    def _sitAt(self, pos, l, r):
        self._rem(l, r)
        self._add(l, pos - 1)
        self._add(pos + 1, r)
    
    def seat(self) -> int:
        # we could sit at the biggest size one (leftmost), or one of the ends potentially
        cands = [] # will hold (score, index to sit, l, r)
        
        # leftmost interval
        leftL, leftR = self.byPos[0]
        if leftL == 0:
            cands.append((leftR + 1, 0, 0, leftR))
        
        # rightmost interval
        rightL, rightR = self.byPos[-1]
        if rightR == self.n - 1:
            cands.append((self.n - rightL, self.n - 1, rightL, rightR))
        
        # biggest interval where we would sit in the middle
        negScore, bigL, bigR = self.bySize[0]
        cands.append((-negScore, (bigL + bigR) // 2, bigL, bigR))
        
        cands.sort(key=lambda c: (-c[0], c[1]))
        score, pos, l, r = cands[0]
        self._sitAt(pos, l, r)
        return pos
    
    def leave(self, p: int) -> None:
        # find the left and right intervals immediately before and after the taken position p
        idx = self.byPos.bisect_left((p, -1))

        leftInterval = self.byPos[idx - 1] if idx > 0 and self.byPos[idx - 1][1] == p - 1 else None
        rightInterval = self.byPos[idx] if idx < len(self.byPos) and self.byPos[idx][0] == p + 1 else None

        # we will conjoin two intervals
        if leftInterval and rightInterval and leftInterval[1] == p - 1 and rightInterval[0] == p + 1:
            self._rem(*leftInterval)
            self._rem(*rightInterval)
            self._add(leftInterval[0], rightInterval[1])
        
        # we join just left
        elif leftInterval and leftInterval[1] == p - 1:
            self._rem(*leftInterval)
            self._add(leftInterval[0], p)
        
        # we join just right
        elif rightInterval and rightInterval[0] == p + 1:
            self._rem(*rightInterval)
            self._add(p, rightInterval[1])
        
        # we join neither
        else:
            self._add(p, p)