# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/generic/GenericSparseTable.py

# e.g. int, str, tuple, ...
RawVal = int

# or can replace this Node type with an entire Node class and it works
Node = tuple


def baseFn(v: RawVal, i: int) -> Node:
    # return (v, v)
    pass


# combine MUST be idempotent: combine(x, x) == x (min, max, gcd, lcm, AND, OR, ... but NOT sum or count)
def combine(left: Node, right: Node) -> Node:
    # return (min(left[0], right[0]), max(left[1], right[1]))
    pass


# A static array (no updates): O(N log N) build, O(1) rangeQuery (one combine call), O(N log N) Nodes of memory
class SparseTable:
    def __init__(self, a, baseFn, combine):
        self.n = n = len(a)
        self.combine = combine
        # t[j][i]: the Node of a[i..i + 2^j - 1], for every i with i + 2^j <= n
        self.t = t = [[baseFn(v, i) for i, v in enumerate(a)]]
        j = 1
        while 2 * (1 << (j - 1)) <= n:
            prev, half = t[-1], 1 << (j - 1)
            t.append([combine(prev[i], prev[i + half]) for i in range(n - 2 * half + 1)])
            j += 1

    # how many elements
    def size(self):
        return self.n

    # the Node of a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError("pointGet: needs 0 <= i < n")
        return self.t[0][i]

    # the Node of a[l..r]: the combine of the two largest power-of-two blocks starting at l and ending at r (they
    # overlap, which is why combine must be idempotent); needs 0 <= l <= r < n, else IndexError
    def rangeQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError("rangeQuery: needs 0 <= l <= r < n")
        j = (r - l + 1).bit_length() - 1
        row = self.t[j]
        if l + (1 << j) - 1 == r:
            return row[l]
        return self.combine(row[l], row[r - (1 << j) + 1])

    # the Node of the whole array; needs n >= 1, else IndexError
    def rangeQueryAll(self):
        if self.n == 0:
            raise IndexError("rangeQueryAll: needs n >= 1")
        return self.rangeQuery(0, self.n - 1)
