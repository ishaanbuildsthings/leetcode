INF = float("inf")

class VersionedMinSeg:
    """
    Persistent min segment tree over values [0, maxVal].

    Each value stores a score; chmin lowers it. snapshot() freezes the
    whole current tree and returns a versionId (0, 1, 2, ... in call
    order); any past version stays queryable. Sparse: an update touches
    only O(log maxVal) nodes, so maxVal can be as large as ~1e9 with raw
    (uncompressed) values -- you pay log(maxVal) per op, so compress when
    you can enumerate the values up front.

        seg = VersionedMinSeg(maxVal)
        seg.chmin(value, score)                    # lower current[value]
        versionId = seg.snapshot()                 # freeze -> version id
        seg.queryVersionMin(versionId, low, high)  # min score over values [low, high]
        seg.queryCurrentMin(low, high)             # same, on the live tree
    """

    # O(1)
    def __init__(self, maxVal):
        self.maxVal = maxVal
        self.left = [0]; self.right = [0]; self.best = [INF]  # node 0 = blank sentinel
        self.cur = 0            # root of the live (unfrozen) tree
        self.versions = [0]     # versions[versionId] -> frozen root; id 0 = blank

    # O(1)
    def _new(self, left, right, best):
        self.left.append(left); self.right.append(right); self.best.append(best)
        return len(self.best) - 1

    # O(log maxVal) time and new nodes -- lowers current[value] to min(old, score)
    def chmin(self, value, score):
        self.cur = self._chmin(self.cur, 0, self.maxVal, value, score)

    # O(1) -- freezes the live tree, returns its versionId
    def snapshot(self):
        self.versions.append(self.cur)
        return len(self.versions) - 1

    # O(log maxVal) -- min score over values [low, high] in the live tree
    # inf if low>high or nothing in range, so if we initialize a tree with values 0...1e9 and then query the min from 1e5...1e6 we get inf
    def queryCurrentMin(self, low, high):
        if low > high: return INF
        return self._query(self.cur, 0, self.maxVal, low, high)

    # O(log maxVal) -- min score over values [low, high] in frozen version `versionId`
    # inf if low>high or nothing in range, so if we initialize a tree with values 0...1e9 and then query the min from 1e5...1e6 we get inf
    def queryVersionMin(self, versionId, low, high):
        if low > high: return INF
        return self._query(self.versions[versionId], 0, self.maxVal, low, high)

    # O(log maxVal) -- rebuilds only the root-to-value path, reuses the rest
    def _chmin(self, node, nodeLow, nodeHigh, value, score):
        if nodeLow == nodeHigh:
            cur = self.best[node]
            return self._new(0, 0, cur if cur <= score else score)
        mid = (nodeLow + nodeHigh) >> 1
        lc, rc = self.left[node], self.right[node]
        if value <= mid:
            lc = self._chmin(lc, nodeLow, mid, value, score)
        else:
            rc = self._chmin(rc, mid + 1, nodeHigh, value, score)
        return self._new(lc, rc, min(self.best[lc], self.best[rc]))

    # O(log maxVal)
    def _query(self, node, nodeLow, nodeHigh, low, high):
        if node == 0 or nodeHigh < low or high < nodeLow:
            return INF
        if low <= nodeLow and nodeHigh <= high:
            return self.best[node]
        mid = (nodeLow + nodeHigh) >> 1
        return min(self._query(self.left[node], nodeLow, mid, low, high),
                   self._query(self.right[node], mid + 1, nodeHigh, low, high))