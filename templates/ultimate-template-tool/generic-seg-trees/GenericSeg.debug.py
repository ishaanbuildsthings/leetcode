# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-seg-trees/GenericSeg.debug.py

DEBUG = True  # print the tree after every operation
TRACE = False  # also print every node the recursion visits
PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED = 64  # longer arrays only print the operation line, not the tree

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


# how a node prints in the debug output
def nodeStr(node: Node) -> str:
    # return f"tot={node[0]} mn={node[1]}"
    return str(node)


def leaf(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


def combine(left: Node, right: Node) -> Node:
    # return (left[0] + right[0], min(left[1], right[1]))
    pass


class Seg:
    def __init__(self, a, leaf, combine):
        self.n = n = len(a)
        self.leaf, self.combine = leaf, combine
        self.tree = [None] * (4 * n)
        if n:
            self._build(1, 0, n - 1, a)
        self._show("build")

    def _build(self, nodeI, tl, tr, a):
        if tl == tr:
            self.tree[nodeI] = self.leaf(a[tl], tl)
            return
        tm = (tl + tr) // 2
        self._build(2 * nodeI, tl, tm, a)
        self._build(2 * nodeI + 1, tm + 1, tr, a)
        self._pull(nodeI)

    def _pull(self, nodeI):
        self.tree[nodeI] = self.combine(self.tree[2 * nodeI], self.tree[2 * nodeI + 1])

    def _trace(self, nodeI, tl, tr, what):
        if TRACE:
            print(f"{'    ' * (nodeI.bit_length() - 1)}[{tl},{tr}] {what}")

    def _show(self, op):
        if not DEBUG:
            return
        print(f"---- {op} ----")
        if 0 < self.n <= PRINT_FULL_TREE_UP_TO_N_OTHERWISE_SIMPLIFIED:
            self._showNode(1, 0, self.n - 1, 0)
        print()

    def _showNode(self, nodeI, tl, tr, depth):
        print(f"{'    ' * depth}[{tl},{tr}] {nodeStr(self.tree[nodeI])}")
        if tl < tr:
            tm = (tl + tr) // 2
            self._showNode(2 * nodeI, tl, tm, depth + 1)
            self._showNode(2 * nodeI + 1, tm + 1, tr, depth + 1)

    def _pointGet(self, nodeI, tl, tr, i):
        self._trace(nodeI, tl, tr, "pointGet: visiting")
        if tl == tr:
            return self.tree[nodeI]
        tm = (tl + tr) // 2
        if i <= tm:
            return self._pointGet(2 * nodeI, tl, tm, i)
        return self._pointGet(2 * nodeI + 1, tm + 1, tr, i)

    def _pointAssign(self, nodeI, tl, tr, i, val):
        self._trace(nodeI, tl, tr, "pointAssign: visiting")
        if tl == tr:
            self.tree[nodeI] = self.leaf(val, i)
            self._trace(nodeI, tl, tr, f"leaf is now {nodeStr(self.tree[nodeI])}")
            return
        tm = (tl + tr) // 2
        if i <= tm:
            self._pointAssign(2 * nodeI, tl, tm, i, val)
        else:
            self._pointAssign(2 * nodeI + 1, tm + 1, tr, i, val)
        self._pull(nodeI)
        self._trace(nodeI, tl, tr, f"pulled: {nodeStr(self.tree[nodeI])}")

    def _rangeQuery(self, nodeI, tl, tr, l, r):
        if l <= tl and tr <= r:
            self._trace(nodeI, tl, tr, f"fully inside: use {nodeStr(self.tree[nodeI])}")
            return self.tree[nodeI]
        tm = (tl + tr) // 2
        if r <= tm:
            self._trace(nodeI, tl, tr, "only the left child overlaps")
            return self._rangeQuery(2 * nodeI, tl, tm, l, r)
        if l > tm:
            self._trace(nodeI, tl, tr, "only the right child overlaps")
            return self._rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r)
        self._trace(nodeI, tl, tr, "splits into both children")
        leftResult = self._rangeQuery(2 * nodeI, tl, tm, l, r)
        rightResult = self._rangeQuery(2 * nodeI + 1, tm + 1, tr, l, r)
        res = self.combine(leftResult, rightResult)
        self._trace(nodeI, tl, tr, f"combined {nodeStr(leftResult)} and {nodeStr(rightResult)} into {nodeStr(res)}")
        return res

    # how many elements
    def size(self):
        return self.n

    # the node of a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError("pointGet: needs 0 <= i < n")
        res = self._pointGet(1, 0, self.n - 1, i)
        self._show(f"pointGet({i}) -> {nodeStr(res)}")
        return res

    # a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError("pointAssign: needs 0 <= i < n")
        self._pointAssign(1, 0, self.n - 1, i, val)
        self._show(f"pointAssign({i}, {val})")

    # the node of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeQuery: needs 0 <= l <= r < n")
        res = self._rangeQuery(1, 0, self.n - 1, l, r)
        self._show(f"rangeQuery({l}, {r}) -> {nodeStr(res)}")
        return res

    # the node of the whole array; needs n >= 1, else IndexError
    def rangeQueryAll(self):
        if self.n == 0:
            raise IndexError("rangeQueryAll: needs n >= 1")
        return self.tree[1]
