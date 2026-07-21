class VersionedSumSeg:
    """
    Persistent sum segment tree over values [0, maxVal].

    Each value stores a count/weight; add() increments it. snapshot()
    freezes the whole current tree and returns a versionId (0, 1, 2, ...
    in call order); any past version stays queryable. Sparse: an update
    touches only O(log maxVal) nodes, so maxVal can be as large as ~1e9
    with raw (uncompressed) values -- you pay log(maxVal) per op, so
    compress when you can enumerate the values up front.

    Unlike max/min, sum has an inverse, so two versions can be DIFFED:
    rangeSumDiff(vHi, vLo, low, high) gives the sum over values
    [low, high] among the items inserted between version vLo and vHi.
    That is the classic persistent-segtree trick (count-in-range,
    kth-smallest). Max/min can't do this -- no inverse to subtract.

        seg = VersionedSumSeg(maxVal)
        seg.add(value, weight)                        # current[value] += weight
        versionId = seg.snapshot()                    # freeze -> version id
        seg.queryVersionSum(versionId, low, high)     # sum over [low, high], one version
        seg.rangeSumDiff(vHi, vLo, low, high)         # sum over (vLo, vHi] items only
    """

    # O(1)
    def __init__(self, maxVal):
        self.maxVal = maxVal
        self.left = [0]; self.right = [0]; self.total = [0]  # node 0 = blank sentinel, sum 0
        self.cur = 0            # root of the live (unfrozen) tree
        self.versions = [0]     # versions[versionId] -> frozen root; id 0 = blank

    # O(1)
    def _new(self, left, right, total):
        self.left.append(left); self.right.append(right); self.total.append(total)
        return len(self.total) - 1

    # O(log maxVal) time and new nodes -- current[value] += weight
    def add(self, value, weight):
        self.cur = self._add(self.cur, 0, self.maxVal, value, weight)

    # O(1) -- freezes the live tree, returns its versionId
    def snapshot(self):
        self.versions.append(self.cur)
        return len(self.versions) - 1

    # O(log maxVal) -- sum over values [low, high] in the live tree
    # 0 if low>high or nothing in range, so a tree over values 0...1e9 queried
    # on 1e5...1e6 with nothing set there returns 0
    def queryCurrentSum(self, low, high):
        if low > high: return 0
        return self._query(self.cur, 0, self.maxVal, low, high)

    # O(log maxVal) -- sum over values [low, high] in frozen version `versionId`
    # 0 if low>high or nothing in range, same 1e9-universe behavior as above
    def queryVersionSum(self, versionId, low, high):
        if low > high: return 0
        return self._query(self.versions[versionId], 0, self.maxVal, low, high)

    # O(log maxVal) -- sum over values [low, high] among items inserted in (vLo, vHi].
    # Requires vLo be an EARLIER version than vHi (vLo's items are a subset).
    # This is the inverse-only capability max/min lack. 0 if low>high.
    def rangeSumDiff(self, vHi, vLo, low, high):
        if low > high: return 0
        return self._queryDiff(self.versions[vHi], self.versions[vLo],
                               0, self.maxVal, low, high)

    # O(log maxVal) -- rebuilds only the root-to-value path, reuses the rest
    def _add(self, node, nodeLow, nodeHigh, value, weight):
        if nodeLow == nodeHigh:
            return self._new(0, 0, self.total[node] + weight)
        mid = (nodeLow + nodeHigh) >> 1
        lc, rc = self.left[node], self.right[node]
        if value <= mid:
            lc = self._add(lc, nodeLow, mid, value, weight)
        else:
            rc = self._add(rc, mid + 1, nodeHigh, value, weight)
        return self._new(lc, rc, self.total[lc] + self.total[rc])

    # O(log maxVal)
    def _query(self, node, nodeLow, nodeHigh, low, high):
        if node == 0 or nodeHigh < low or high < nodeLow:
            return 0
        if low <= nodeLow and nodeHigh <= high:
            return self.total[node]
        mid = (nodeLow + nodeHigh) >> 1
        return (self._query(self.left[node], nodeLow, mid, low, high) +
                self._query(self.right[node], mid + 1, nodeHigh, low, high))

    # O(log maxVal) -- descend both roots subtracting; the subtraction is what
    # recovers exactly the items in (vLo, vHi]. Only valid because sum inverts.
    def _queryDiff(self, hiNode, loNode, nodeLow, nodeHigh, low, high):
        if nodeHigh < low or high < nodeLow:
            return 0
        if low <= nodeLow and nodeHigh <= high:
            return self.total[hiNode] - self.total[loNode]
        mid = (nodeLow + nodeHigh) >> 1
        return (self._queryDiff(self.left[hiNode], self.left[loNode], nodeLow, mid, low, high) +
                self._queryDiff(self.right[hiNode], self.right[loNode], mid + 1, nodeHigh, low, high))