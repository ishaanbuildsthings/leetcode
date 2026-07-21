# TEMPLATE BY ISHAANBUILDSTHINGS (see my github)

NEG = float('-inf')

class OnlineSparseBIT2DMax:
    """
    Fully online sparse 2D Binary Indexed Tree over a max monoid:
      - chmax:    tree[x][y] = max(tree[x][y], v)
      - queryMax: max over a corner-anchored rectangle, orientation set
                  per axis at construction via descX / descY

    Coordinates may be arbitrary integers in [loX, hiX] x [loY, hiY];
    shifts are handled internally. Backed by dicts, so no coordinates
    need to be known in advance and no O(uX * uY) array is allocated.

    ORIENTATION IS FIXED AT CONSTRUCTION. descX / descY reverse an axis
    internally, turning that axis's suffix query into a prefix query.
    This cannot be a per-call option: chmax writes into node ranges
    determined by the orientation, so a tree built ascending contains no
    node covering a suffix. Choose per axis up front.

    Queries are always CORNER-ANCHORED. Max has no inverse, so an
    interior rectangle cannot be obtained by diffing prefixes. Orient
    the axes so every query you need is anchored.

    MONOTONE UPDATES ONLY. A cell can be raised, never lowered; a
    decrease is silently ignored, not applied. Internal nodes store a
    winner and forget the runners-up, so a decrease is unrecoverable.

    Complexities in terms of universe sizes uX, uY (coordinate ranges),
    with P = number of distinct chmax calls performed:
      __init__:  O(1)
      chmax:     O(log(uX) * log(uY)) time
      queryMax:  O(log(uX) * log(uY)) time
      memory:    O(P * log(uX) * log(uY)) entries

    Memory is the binding constraint: each chmax materializes up to
    log(uX) * log(uY) dict entries. At uX = uY = 1e5 that is ~289 per
    update, so this is comfortable to ~1e4 updates and will MLE well
    before 1e5. When all update coordinates are knowable in advance,
    the offline variant compresses each row node's column set and costs
    only log(uX) slots per point instead.
    """

    # O(1)
    def __init__(self, loX, hiX, loY, hiY, descX=False, descY=False):
        self.loX = loX
        self.hiX = hiX
        self.loY = loY
        self.hiY = hiY
        self.descX = descX
        self.descY = descY
        self.uX = hiX - loX + 1
        self.uY = hiY - loY + 1
        self.t = {}                       # rowNode -> {colNode: maxVal}

    # O(log(uX) * log(uY))
    def chmax(self, x, y, v):
        """tree[x][y] = max(tree[x][y], v). Never lowers a cell."""
        # map user coords to internal 1..u, reversing a descending axis
        #   asc:  loX -> 1,  hiX -> uX
        #   desc: hiX -> 1,  loX -> uX
        x = self.hiX - x + 1 if self.descX else x - self.loX + 1
        y = self.hiY - y + 1 if self.descY else y - self.loY + 1
        t = self.t
        uX = self.uX
        uY = self.uY
        while x <= uX:                    # every row node covering x
            row = t.get(x)
            if row is None:
                row = t[x] = {}
            j = y
            while j <= uY:                # every col node covering y
                cur = row.get(j)
                if cur is None or cur < v:
                    row[j] = v
                j += j & -j
            x += x & -x

    # O(log(uX) * log(uY))
    def queryMax(self, x, y):
        """Max over the corner rectangle bounded by x and y, per the
        descX / descY orientation set at construction.

        Orientation determines which side of each axis the rectangle is
        anchored to. The passed bound is always the free (open) edge:

            descX  descY   queryMax(x, y) covers
            -----  -----   ---------------------
            False  False   [loX, x] x [loY, y]     both prefixes
            False  True    [loX, x] x [y, hiY]     prefix, suffix
            True   False   [x, hiX] x [loY, y]     suffix, prefix
            True   True    [x, hiX] x [y, hiY]     both suffixes

        Concretely, with loX=0, hiX=9, loY=1, hiY=100:

            descX=False, descY=False:
                queryMax(4, 50)  -> indices 0..4,  values 1..50
            descX=False, descY=True:
                queryMax(4, 50)  -> indices 0..4,  values 50..100
            descX=True,  descY=False:
                queryMax(4, 50)  -> indices 4..9,  values 1..50
            descX=True,  descY=True:
                queryMax(4, 50)  -> indices 4..9,  values 50..100

        Typical use: to find the best predecessor at index <= i-k with
        value strictly greater than v, build with descY=True and call
        queryMax(i - k, v + 1).

        Bounds are clamped, so out-of-range args are safe:
            ascending axis,  bound < lo   -> empty, contributes NEG
            ascending axis,  bound > hi   -> full axis
            descending axis, bound > hi   -> empty, contributes NEG
            descending axis, bound < lo   -> full axis

        Returns NEG if the rectangle is empty or no cell in it has been
        written, so callers need no bounds guard.
        """
        x = self.hiX - x + 1 if self.descX else x - self.loX + 1
        y = self.hiY - y + 1 if self.descY else y - self.loY + 1
        if x <= 0 or y <= 0:
            return NEG
        uX = self.uX
        uY = self.uY
        if x > uX: x = uX
        if y > uY: y = uY
        t = self.t
        best = NEG
        while x > 0:                      # disjoint row blocks tiling [1..x]
            row = t.get(x)
            if row is not None:           # skip whole row node if never written
                j = y
                while j > 0:              # disjoint col blocks tiling [1..y]
                    cur = row.get(j)
                    if cur is not None and cur > best:
                        best = cur
                    j -= j & -j
            x -= x & -x
        return best