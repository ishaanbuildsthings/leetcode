# TEMPLATE BY ISHAANBUILDSTHINGS (see my github)

from bisect import bisect_left, bisect_right

NEG = float('-inf')

class OfflineSparseBIT2DMax:
    """
    Offline sparse 2D Binary Indexed Tree over a max monoid:
      - chmax:    tree[x][y] = max(tree[x][y], v)
      - queryMax: max over a corner-anchored rectangle, orientation set
                  per axis at construction via descX / descY

    ALL update coordinates must be passed to the constructor. chmax at
    an unregistered (x, y) is undefined behaviour. That requirement is
    what buys the memory: each row node stores only the y-coords that
    actually occur inside it, sorted, with a dense inner Fenwick over
    that compressed list. A point costs log(uX) slots instead of the
    online variant's log(uX) * log(uY) -- ~34x fewer entries at
    uX = uY = 1e5, in flat lists rather than dicts.

    ORIENTATION IS FIXED AT CONSTRUCTION. descX / descY reverse an axis
    internally, turning that axis's suffix query into a prefix query.
    This cannot be a per-call option: chmax writes into node ranges
    determined by the orientation, so a tree built ascending contains no
    node covering a suffix. Choose per axis up front.

        descX  descY   queryMax(x, y) covers
        -----  -----   ---------------------
        False  False   [loX, x] x [loY, y]     both prefixes
        False  True    [loX, x] x [y, hiY]     prefix, suffix
        True   False   [x, hiX] x [loY, y]     suffix, prefix
        True   True    [x, hiX] x [y, hiY]     both suffixes

    Queries are always CORNER-ANCHORED. Max has no inverse, so an
    interior rectangle cannot be obtained by diffing prefixes.

    MONOTONE UPDATES ONLY. A cell can be raised, never lowered; a
    decrease is silently ignored, not applied.

    With P = len(points), universe sizes uX, uY:
      __init__:  O(P log P + P log(uX)) time, O(P log(uX)) memory
      chmax:     O(log(uX) * log(uY))
      queryMax:  O(log(uX) * log(uY))
    """

    def __init__(self, loX, hiX, loY, hiY, points, descX=False, descY=False):
        self.loX = loX
        self.hiX = hiX
        self.loY = loY
        self.hiY = hiY
        self.descX = descX
        self.descY = descY
        uX = hiX - loX + 1
        uY = hiY - loY + 1
        self.uX = uX
        self.uY = uY

        # map to internal 1..u once, then sort by y so every bucket comes
        # out already sorted -- no per-node sort needed, just dedup on append
        mapped = []
        for x, y in points:
            mx = hiX - x + 1 if descX else x - loX + 1
            my = hiY - y + 1 if descY else y - loY + 1
            mapped.append((my, mx))
        mapped.sort()

        buckets = [None] * (uX + 2)
        for my, mx in mapped:
            i = mx
            while i <= uX:                 # register y in every row node covering x
                b = buckets[i]
                if b is None:
                    buckets[i] = [my]
                elif b[-1] != my:
                    b.append(my)
                i += i & -i

        start = [0] * (uX + 2)             # node i owns ys[start[i] : start[i+1]]
        ys = []
        for i in range(1, uX + 1):
            start[i] = len(ys)
            b = buckets[i]
            if b:
                ys.extend(b)
        start[uX + 1] = len(ys)

        self.start = start
        self.ys = ys
        self.dat = [NEG] * len(ys)

    # O(log(uX) * log(uY))
    def chmax(self, x, y, v):
        """tree[x][y] = max(tree[x][y], v). Never lowers a cell."""
        x = self.hiX - x + 1 if self.descX else x - self.loX + 1
        y = self.hiY - y + 1 if self.descY else y - self.loY + 1
        ys = self.ys
        dat = self.dat
        start = self.start
        uX = self.uX
        while x <= uX:
            a = start[x]
            b = start[x + 1]
            size = b - a
            j = bisect_left(ys, y, a, b) - a + 1      # 1-indexed within node
            while j <= size:
                p = a + j - 1
                if dat[p] < v:
                    dat[p] = v
                j += j & -j
            x += x & -x

    # O(log(uX) * log(uY))
    def queryMax(self, x, y):
        """Max over the corner rectangle bounded by x and y, per the
        descX / descY orientation. Bounds are clamped, so out-of-range
        args are safe. NEG if empty or untouched -- no caller guard."""
        x = self.hiX - x + 1 if self.descX else x - self.loX + 1
        y = self.hiY - y + 1 if self.descY else y - self.loY + 1
        if x <= 0 or y <= 0:
            return NEG
        uX = self.uX
        uY = self.uY
        if x > uX: x = uX
        if y > uY: y = uY
        ys = self.ys
        dat = self.dat
        start = self.start
        best = NEG
        while x > 0:
            a = start[x]
            b = start[x + 1]
            j = bisect_right(ys, y, a, b) - a         # count of cols <= y
            while j > 0:
                p = a + j - 1
                cur = dat[p]
                if cur > best:
                    best = cur
                j -= j & -j
            x -= x & -x
        return best