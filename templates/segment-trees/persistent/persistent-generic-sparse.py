# EXAMPLE
#
# NodeData is usually a tuple or a plain number.
#
# def base(rawVal) -> NodeData:
#     return rawVal
#
# how to aggregate two NodeData nodes (never receives None)
# def mergeFn(a, b) -> NodeData:
#     return a if a > b else b                   # max
#     # return a + b                             # sum
#     # return (min(a[0],b[0]), max(a[1],b[1]))  # min-and-max tuple


# TO CREATE (sparse over values [0, maxVal])
# seg = PersistentSeg(maxVal, base, mergeFn)


# METHODS
#
# O(log maxVal) -- pointSet(value, rawVal): overwrite value's data with base(rawVal)
#   in the live tree. For chmax: query the value first, set only if larger.
# O(1)          -- snapshot() -> versionId (0, 1, 2, ... in call order); freezes live tree
# O(log maxVal) -- queryCurrent(low, high) -> NodeData | None: aggregate over the live
#   tree; None if low > high OR nothing is set in [low, high]
# O(log maxVal) -- queryVersion(versionId, low, high) -> NodeData | None: same, on a
#   frozen version


class PersistentSeg:
    # sparse over values [0, maxVal]; base wraps a raw value, combine merges two datas
    def __init__(self, maxVal, base, combine):
        self.maxVal = maxVal
        self.base = base
        self.combine = combine
        self.left = [0]        # left[node]  -> left child index;  node 0 = empty sentinel
        self.right = [0]       # right[node] -> right child index
        self.data = [None]     # data[node]  -> aggregate; data[0] = None = empty subtree
        self.cur = 0           # root index of the live (unfrozen) tree
        self.versions = [0]    # versions[versionId] -> frozen root; id 0 = blank tree

    # merge two datas, treating None as "empty" so combine never sees it
    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)

    # allocate a fresh node, return its index (this is what makes it persistent)
    def _new(self, left, right, data):
        self.left.append(left)
        self.right.append(right)
        self.data.append(data)
        return len(self.data) - 1

    # overwrite the data at `value` in the live tree with base(rawVal)
    def pointSet(self, value, rawVal):
        self.cur = self._set(self.cur, 0, self.maxVal, value, self.base(rawVal))

    # freeze the current live tree; later queryVersion calls can read it forever
    def snapshot(self):
        self.versions.append(self.cur)
        return len(self.versions) - 1

    # aggregate over [low, high] in the live tree; None if empty range or nothing set, so if we initialize a seg tree with value range 0...1e9 and then query 1e5...1e6 we get None
    def queryCurrent(self, low, high):
        if low > high: return None
        return self._query(self.cur, 0, self.maxVal, low, high)

    # aggregate over [low, high] in a frozen version; None if empty range or nothing set, so if we initialize a seg tree with value range 0...1e9 and then query 1e5...1e6 we get None
    def queryVersion(self, versionId, low, high):
        if low > high: return None
        return self._query(self.versions[versionId], 0, self.maxVal, low, high)

    # rebuild only the root->value path into new nodes, reuse every off-path child
    def _set(self, node, nodeLow, nodeHigh, value, newData):
        if nodeLow == nodeHigh:
            return self._new(0, 0, newData)
        mid = (nodeLow + nodeHigh) >> 1
        lc, rc = self.left[node], self.right[node]
        if value <= mid:
            lc = self._set(lc, nodeLow, mid, value, newData)
        else:
            rc = self._set(rc, mid + 1, nodeHigh, value, newData)
        return self._new(lc, rc, self._combineOpt(self.data[lc], self.data[rc]))

    # standard range aggregate; node 0 (empty subtree) contributes None
    def _query(self, node, nodeLow, nodeHigh, low, high):
        if node == 0 or nodeHigh < low or high < nodeLow:
            return None
        if low <= nodeLow and nodeHigh <= high:
            return self.data[node]
        mid = (nodeLow + nodeHigh) >> 1
        return self._combineOpt(
            self._query(self.left[node], nodeLow, mid, low, high),
            self._query(self.right[node], mid + 1, nodeHigh, low, high))