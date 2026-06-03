# Template by leetgoat_dot_dev (leetcode) ishaanbuildsthings (github)
# (_(
# /_/'_____/)
# "  |      |
#    |""""""|

# ✅
# Benchmarked on https://leetcode.com/contest/weekly-contest-452/problems/maximize-count-of-distinct-primes-after-split/description/, passes in 4.5s
# All methods tested via in-house test suite
# A few methods are not optimized such as the walks, but overall things should be very fast

# Iterative 2N + padding tree, walks are recursive though
# Left child: 2*i, right child: 2*i+1
# Lazy tag means the current node value has been updated, but not yet pushed to children

# Build - O(n)
# Range add - O(logN)
# Query max - O(logN)
# Query all - O(1)
# Point assign - O(logN)
# Query point - O(logN)
# Leftmost index GTE X in a range - O(logN)
# Rightmost index GTE X in a range - O(logN)
# Find leftmost index of max element in a range - O(logN)
# Find rightmost index of max element in a range - O(logN)

fmax = lambda x, y: x if x > y else y
NINF = -10**18
class RangeAddRangeMax:
    __slots__ = ('n', 'N', 'height', 'tree', 'lazyAdd')

    # O(n) build time
    def __init__(self, arr):
        self.n = len(arr)
        if self.n == 0:
            self.N = 1
            self.height = 1
            self.tree  = [NINF, NINF]
            self.lazyAdd = [0, 0]
            return

        self.N = 1 << (self.n - 1).bit_length() # Pad the tree to the next power of 2, seems to be needed for lazy trees, but also if we don't do this I think the nodes get weird and represent non-contiguous ranges
        self.height = self.N.bit_length() - 1

        tree = [NINF] * (2 * self.N)

        # Seed the leaf nodes
        tree[self.N : self.N + self.n] = arr
        # Build the non-leaf nodes
        for i in range(self.N - 1, 0, -1):
            tree[i] = fmax(tree[i << 1], tree[i << 1 | 1])

        self.tree  = tree
        self.lazyAdd = [0] * (self.N) # Leaf nodes don't have lazy tags, optimization

    # Starts at the parent of a node, updates that parent based on the children and then moves up more
    # For instance if we update a point we need to pull up after
    # O(logN)
    def _pullUp(self, i):
        tree, lazyAdd = self.tree, self.lazyAdd
        i >>= 1
        while i:
            tree[i] = fmax(tree[i << 1], tree[i << 1 | 1]) + lazyAdd[i]
            i >>= 1

    # Flush out lazy tag updates down to the leaf node, goes from root to node, O(logN)
    def _pushDown(self, node):
        tree, lazyAdd, N = self.tree, self.lazyAdd, self.N
        for height in range(self.height, 0, -1):
            i = node >> height
            # If we have a lazy tag, flush it to its children, updating the children values and lazy tags
            if lazyAdd[i]:
                add = lazyAdd[i]
                lazyAdd[i] = 0

                left = i << 1
                right = left | 1

                tree[left] += add
                tree[right] += add
                if left < N:
                    lazyAdd[left] += add
                if right < N:
                    lazyAdd[right] += add


    # Adds val to every element in inclusive [ql, qr], O(logN)
    def rangeAdd(self, ql, qr, val):
        if val == 0 or ql > qr:
            return
        N, tree, lazyAdd = self.N, self.tree, self.lazyAdd
        # Initial leaf node indices in the tree / lazyAdd arrays
        l0, r0 = ql + N, qr + N

        # These are indices that eventually meet at a segment tree node
        L, R = l0, r0

        # handle leaves separately which don't do lazy tag updates, avoid an if branch
        if L & 1:
            tree[L] += val
        L += 1
        if not (R & 1):
            tree[R] += val
        R -= 1
        L //= 2
        R //= 2

        # handle non leaf nodes
        while L <= R:
            # If L is a right child, we are forced to use it since we cannot use its parent
            if L & 1:
                tree[L] += val
                lazyAdd[L] += val
                L += 1
            # If R is a left child, we are forced to use it since we cannot use its parent
            if not (R & 1):
                tree[R] += val
                lazyAdd[R] += val
                R -= 1
            # Move up the tree
            L //= 2
            R //= 2

        # Don't understand the logic here of why we only pull up the two endpoints but it is likely similar to what we do in queryMax logic explanation
        self._pullUp(l0)
        self._pullUp(r0)

    # Returns the maximum value in the range [ql, qr], O(logN)
    def queryMax(self, ql, qr):
        if ql > qr:
            return NINF

        N, tree = self.N, self.tree
        # Initial leaf node indices in the tree / lazyAdd arrays
        l0, r0 = ql + N, qr + N

        # I'm not fully convinced of this logic yet but the general idea I believe is:
        # We need to push out any updates down to the two endpoints before we query things, so those are updated
        # but what about nodes that will be used in our query that aren't along one of these two paths?
        # i.e. we query [1, 4] and our nodes are [1, 1] [2, 3] [4, 4] where [2, 3] isn't on one path
        # since the [2, 3] node is fully contained, and tree[i] stores non-stale values after the i-th lazy tag is already applied to that node, we can just grab the value from that node directly and no pushing is needed
        # but in endpoint paths with partial overlaps, we need to keep going down below and thus need to push
        self._pushDown(l0)
        self._pushDown(r0)

        res = NINF
        L, R = l0, r0

        while L <= R:
            # If L is a right child, we are forced to use it since we cannot use its parent
            if L & 1:
                res = fmax(res, tree[L])
                L += 1
            # If R is a left child, we are forced to use it since we cannot use its parent
            if not (R & 1):
                res = fmax(res, tree[R])
                R -= 1
            # Move up the tree
            L //= 2
            R //= 2
        return res

    # Queries the entire region in O(1)
    def queryAll(self):
        return self.tree[1]

    # Sets the value at the index, O(logN)
    def pointAssign(self, index, val):
        node = index + self.N
        # We need to flush out updates first, otherwise if we directly update the leaf node, its parents will still have lazy tags which would later get sent back down to this leaf again!
        # Think of this like "commit every deferred update to this leaf before we do anything else, otherwise those commits would later overwrite the new value we are trying to set"
        self._pushDown(node)
        # Update the node value directly
        self.tree[node] = val
        # Pull up to update ancestors
        self._pullUp(node)

    # Gets the value at the index, O(logN) since it is a lazy tree
    def queryPoint(self, index):
        node = index + self.N
        # We need to flush out the updates to this point first, otherwise the value at this point would be stale
        self._pushDown(node)
        return self.tree[node]

    def printDiagram(self):
        if self.n == 0:
            print("<empty tree>")
            return

        tree, lazy = self.tree, self.lazyAdd
        N, n = self.N, self.n

        def _print(node, l, r, prefix, isLast):
            # Skip padded segments that lie completely outside [0, n-1]
            if l >= n:
                return

            lazyStr = f"lazy={lazy[node]}" if node < self.N else ""

            connector = "└──" if isLast else "├──"
            print(f"{prefix}{connector}[{l}, {min(r, n-1)}]  "
                  f"v={tree[node] if tree[node] != NINF else 'NINF'}  "
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

    # Find leftmost index in [ql, qr] where element >= val, returns -1 if not found, recursive walk
    # UNOPTIMIZED
    # O(logN)
    def leftmostIdxGTEX(self, ql, qr, val):
        if ql > qr:
            return -1
        return self._leftmostIdxGTEXHelper(1, 0, self.N, ql, qr + 1, val)

    def _leftmostIdxGTEXHelper(self, node, tl, tr, ql, qr, val):
        # No intersection
        if qr <= tl or tr <= ql:
            return -1

        # Check if this segment's maximum is less than val
        current_max = self.tree[node]
        if current_max < val:
            return -1

        # Push down lazy values if needed
        if node < self.N and self.lazyAdd[node]:
            add = self.lazyAdd[node]
            self.lazyAdd[node] = 0

            left = node << 1
            right = left | 1

            self.tree[left] += add
            self.tree[right] += add
            if left < self.N:
                self.lazyAdd[left] += add
            if right < self.N:
                self.lazyAdd[right] += add

        # Leaf node
        if node >= self.N:
            leafIdx = node - self.N
            if ql <= leafIdx < qr and leafIdx < self.n:
                return leafIdx
            return -1

        tm = (tl + tr) >> 1

        # Try left child first
        leftResult = self._leftmostIdxGTEXHelper(node << 1, tl, tm, ql, qr, val)
        if leftResult != -1:
            return leftResult

        # Try right child
        return self._leftmostIdxGTEXHelper(node << 1 | 1, tm, tr, ql, qr, val)

    # Find rightmost index in [ql, qr] where element >= val, returns -1 if not found, recursive walk
    # UNOPTIMIZED
    # O(logN)
    def rightmostIdxGTEX(self, ql, qr, val):
        if ql > qr:
            return -1
        return self._rightmostIdxGTEXHelper(1, 0, self.N, ql, qr + 1, val)

    def _rightmostIdxGTEXHelper(self, node, tl, tr, ql, qr, val):
        # No intersection or max in this segment < val
        if qr <= tl or tr <= ql or self.tree[node] < val:
            return -1

        # Push down lazy values if needed
        if node < self.N and self.lazyAdd[node]:
            add = self.lazyAdd[node]
            self.lazyAdd[node] = 0

            left = node << 1
            right = left | 1

            self.tree[left] += add
            self.tree[right] += add
            if left < self.N:
                self.lazyAdd[left] += add
            if right < self.N:
                self.lazyAdd[right] += add

        # Leaf node
        if node >= self.N:
            leafIdx = node - self.N
            if ql <= leafIdx < qr and leafIdx < self.n:
                return leafIdx
            return -1

        tm = (tl + tr) >> 1

        # Try right child first for rightmost
        rightResult = self._rightmostIdxGTEXHelper(node << 1 | 1, tm, tr, ql, qr, val)
        if rightResult != -1:
            return rightResult

        # Try left child
        return self._rightmostIdxGTEXHelper(node << 1, tl, tm, ql, qr, val)

    # Find leftmost index of maximum element in a range, returns -1 if not found, recursive walk
    # UNOPTIMIZED (can maybe do 1 logN call instead of 2?)
    # O(logN)
    def findMaxIndexLeft(self, ql, qr):
        if ql > qr:
            return -1
        # First find the maximum value in the range
        maxVal = self.queryMax(ql, qr)
        # Then find the leftmost index with that value
        return self.leftmostIdxGTEX(ql, qr, maxVal)

    # Find rightmost index of maximum element in a range, returns -1 if not found
    # UNOPTIMIZED (can maybe do 1 logN call instead of 2?)
    # O(logN)
    def findMaxIndexRight(self, ql, qr):
        if ql > qr:
            return -1
        # First find the maximum value in the range
        maxVal = self.queryMax(ql, qr)
        # Then find the rightmost index with that value
        return self.rightmostIdxGTEX(ql, qr, maxVal)


import sys
input = sys.stdin.readline

n, m = map(int, input().split())
arr = list(map(int, input().split()))
st = RangeAddRangeMax(arr)
for _ in range(m):
    query = list(map(int, input().split()))
    if query[0] == 1:
        st.pointAssign(query[1], query[2])
    else:
        print(st.leftmostIdxGTEX(0, len(arr) - 1, query[1]))