# Template by leetgoat_dot_dev (leetcode) ishaanbuildsthings (github)
# (_(
# /_/'_____/)
# "  |      |
#    |""""""|

# All methods tested via in-house test suite
# Not as optimized as the RangeAdd.RangeMin for example, since that was pulled from someone's CF submission. This however is based on that and adapted to support assign/sum, so it should still be fast as it has lots of optimizations.

# Iterative 2N + padding tree
# Left child: 2*i, right child: 2*i+1
# Lazy tag means the current node value has been updated, but not yet pushed to children

# Build - O(n)
# Range assign - O(logN)
# Query sum - O(logN)
# Query all - O(1)
# Point assign - O(logN)
# Query point - O(logN)
# Leftmost prefix sum gte x when all numbers gte zero - O(logN)
# Are all values in range [l...r] the same - O(logN)

_NO_TAG = None
class RangeAssignRangeSum:
    __slots__ = ('n', 'N', 'height', 'tree', 'lazyAssign', 'nodeSize')

    # O(n) build time
    def __init__(self, arr):
        self.n = len(arr)
        if self.n == 0:
            self.N = 1
            self.height = 1
            self.tree = [0, 0]
            self.lazyAssign = [_NO_TAG]
            self.nodeSize = [1, 1] # choosing to prestore node sizes which is needed for assign+sum, but not sure if this is faster than calculating on the fly
            return

        self.N = 1 << (self.n - 1).bit_length() # Pad the tree to the next power of 2, seems to be needed for lazy trees, but also if we don't do this I think the nodes get weird and represent non-contiguous ranges
        self.height = self.N.bit_length() - 1

        N = self.N
        tree = [0] * (2 * N)
        nodeSize = [0] * (2 * N)
        lazyAssign = [_NO_TAG] * N

        # Seed the leaf nodes
        tree[N : N + self.n] = arr
        # Seed the leaf sizes
        for i in range(self.n):
            nodeSize[N + i] = 1

        # Build the non-leaf nodes + sizes
        for i in range(N - 1, 0, -1):
            nodeSize[i] = nodeSize[i << 1] + nodeSize[i << 1 | 1]
            tree[i] = tree[i << 1] + tree[i << 1 | 1]

        self.tree, self.lazyAssign, self.nodeSize = tree, lazyAssign, nodeSize

    # Applies an assign tag to a tree node by applying the value and putting a lazy tag for children, O(1)
    def _apply(self, node, value):
        self.tree[node] = value * self.nodeSize[node]
        if node < self.N:
            self.lazyAssign[node] = value

    # Flushes out lazy tag updates down to the leaf node, goes from root to node, O(logN)
    def _pushDown(self, node):
        tree, lazyAssign, nodeSize, N = self.tree, self.lazyAssign, self.nodeSize, self.N
        for height in range(self.height, 0, -1):
            i = node >> height
            lazyVal = lazyAssign[i]
            if lazyVal is _NO_TAG:
                continue
            left = i << 1
            right = i << 1 | 1
            tree[left] = lazyVal * nodeSize[left]
            tree[right] = lazyVal * nodeSize[right]
            if left < N:
                lazyAssign[left] = lazyVal
            if right < N:
                lazyAssign[right] = lazyVal
            lazyAssign[i] = _NO_TAG

    # Starts at the parent of a node, updates that parent based on the children and then moves up more
    # For instance if we update a point we need to pull up after
    # O(logN)
    def _pullUp(self, node):
        tree, lazyAssign = self.tree, self.lazyAssign
        while node > 1:
            node >>= 1
            # Confused about this
            if lazyAssign[node] is _NO_TAG:
                tree[node] = tree[node<<1] + tree[node<<1|1]

    # Assigns all values in the range [ql, qr] to val, O(logN)
    def rangeAssign(self, ql, qr, val):
        if ql > qr:
            return
        N = self.N
        l0, r0 = ql + N, qr + N

        # This part is weird
        # We don't have these pushes in things like RangeAdd.RangeMin tree and that seems to work
        # If we keep these pushes, we can supposedly support range assign to 1 and range sum since I passed LC 2158 amount of new area painted, without these, MUCH faster
        # but I think that's just because we were only assigning the same value each time?
        # either way, there is some magic or secret simpler queries like only point queries or only assign to 1 ever that allows us to sometimes remove this for a speed up
        # so if we are in TLE, we could try removing this and see what happens...
        self._pushDown(l0)
        self._pushDown(r0)
        L, R = l0, r0

        # Handle leaves separately which don't do lazy tag updates, avoid an if branch
        if L & 1:
            self._apply(L, val)
            L += 1
        if not (R & 1):
            self._apply(R, val)
            R -= 1
        L >>= 1
        R >>= 1

        # handle non leaf nodes
        while L <= R:
            # If L is a right child, we are forced to use it since we cannot use its parent
            if L & 1:
                self._apply(L, val)
                L += 1
            # If R is a left child, we are forced to use it since we cannot use its parent
            if not (R & 1):
                self._apply(R, val)
                R -= 1
            # Move up the tree
            L >>= 1
            R >>= 1

        # Don't understand the logic here of why we only pull up the two endpoints but it is likely similar to what we do in queryMax logic explanation
        self._pullUp(l0)
        self._pullUp(r0)

    # Returns the sum of the range [ql, qr], O(logN)
    def querySum(self, ql, qr):
        if ql > qr:
            return 0
        N = self.N
        l0, r0 = ql + N, qr + N
        self._pushDown(l0)
        self._pushDown(r0)
        L, R = l0, r0

        res = 0
        while L <= R:
            if L & 1:
                res += self.tree[L]
                L += 1
            if not (R & 1):
                res += self.tree[R]
                R -= 1
            L >>= 1
            R >>= 1
        return res

    # Queries the sum of the entire region O(1)
    def queryAll(self):
        return self.tree[1]

    # Sets the value at the index, O(logN)
    def pointAssign(self, idx, val):
        node = idx + self.N
        # We need to flush out updates first, otherwise if we directly update the leaf node, its parents will still have lazy tags which would later get sent back down to this leaf again!
        # Think of this like "commit every deferred update to this leaf before we do anything else, otherwise those commits would later overwrite the new value we are trying to set"
        # Also
        # I'm not fully convinced of this logic yet but the general idea I believe is:
        # We need to push out any updates down to the two endpoints before we query things, so those are updated
        # but what about nodes that will be used in our query that aren't along one of these two paths?
        # i.e. we query [1, 4] and our nodes are [1, 1] [2, 3] [4, 4] where [2, 3] isn't on one path
        # since the [2, 3] node is fully contained, and tree[i] stores non-stale values after the i-th lazy tag is already applied to that node, we can just grab the value from that node directly and no pushing is needed
        # but in endpoint paths with partial overlaps, we need to keep going down below and thus need to push
        self._pushDown(node)
        # Update the node value directly
        self.tree[node] = val
        # Pull up to update ancestors
        self._pullUp(node)

    # Gets the value at the index, O(logN) since it is a lazy tree
    def queryPoint(self, idx):
        node = idx + self.N
        # We need to flush out the updates to this point first, otherwise the value at this point would be stale
        self._pushDown(node)
        return self.tree[node]

    # Returns the leftmost index such that the elements in [0...idx] are >= X, O(logN)
    def leftmostPrefixSumGteXWhenAllNumbersGTEZero(self, x):
        pass # TODO https://cp-algorithms.com/data_structures/segment_tree.html#searching-for-an-array-prefix-with-a-given-amount

    def areAllValuesInRangeUniform(self, ql, qr):
        pass # TODO I think this is doable with an assignment segment tree

    def printDiagram(self):
        if self.n == 0:
            print("<empty tree>")
            return

        tree, lazyAssign = self.tree, self.lazyAssign
        N, n = self.N, self.n

        def _print(node, l, r, prefix, isLast):
            # Skip padded segments that lie completely outside [0, n-1]
            if l >= n:
                return

            lazyStr = f"lazy={lazyAssign[node]}" if node < self.N else ""

            connector = "└──" if isLast else "├──"
            print(f"{prefix}{connector}[{l}, {min(r, n-1)}]  "
                    f"v={tree[node]}  "
                    f"{lazyStr}")

            # Stop at leaves
            if node >= N:
                return

            mid = (l + r) >> 1
            # prepare prefixes for children
            new_prefix = prefix + ("    " if isLast else "│   ")

            # left child is "not last" unless right child is skipped
            right_child_skipped = mid + 1 >= n
            _print(node << 1, l, mid, new_prefix, right_child_skipped)
            if not right_child_skipped:
                _print(node << 1 | 1, mid + 1, r, new_prefix, True)

        # root covers [0, N-1]
        _print(1, 0, N - 1, "", True)


import sys
input = sys.stdin.readline

n, m = map(int, input().split())
arr = [0] * n
st = RangeAssignRangeSum(arr)

for _ in range(m):
    query = list(map(int, input().split()))
    if query[0] == 1:
        l, r, v = query[1:]
        r -= 1
        st.rangeAssign(l, r, v)
    else:
        l, r = query[1:]
        r -= 1
        print(st.querySum(l, r))