standard_input, packages, output_together = 1, 1, 0
dfs, hashing, read_from_file = 1, 0, 0
de = 0

if 1:

    if standard_input:
        import io, os, sys
        input = lambda: sys.stdin.readline().strip()

        import math
        inf = math.inf

        def I():
            return input()

        def II():
            return int(input())

        def MII():
            return map(int, input().split())

        def LI():
            return input().split()

        def LII():
            return list(map(int, input().split()))

        def LFI():
            return list(map(float, input().split()))

        def GMI():
            return map(lambda x: int(x) - 1, input().split())

        def LGMI():
            return list(map(lambda x: int(x) - 1, input().split()))

    if packages:
        from io import BytesIO, IOBase

        import random
        import os

        import bisect
        import typing
        from collections import Counter, defaultdict, deque
        from copy import deepcopy
        from functools import cmp_to_key, lru_cache, reduce
        from heapq import merge, heapify, heappop, heappush, heappushpop, nlargest, nsmallest
        from itertools import accumulate, combinations, permutations, count, product
        from operator import add, iand, ior, itemgetter, mul, xor
        from string import ascii_lowercase, ascii_uppercase, ascii_letters
        from typing import *
        BUFSIZE = 4096

    if output_together:
        class FastIO(IOBase):
            newlines = 0

            def __init__(self, file):
                self._fd = file.fileno()
                self.buffer = BytesIO()
                self.writable = "x" in file.mode or "r" not in file.mode
                self.write = self.buffer.write if self.writable else None

            def read(self):
                while True:
                    b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                    if not b:
                        break
                    ptr = self.buffer.tell()
                    self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
                self.newlines = 0
                return self.buffer.read()

            def readline(self):
                while self.newlines == 0:
                    b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
                    self.newlines = b.count(b"\n") + (not b)
                    ptr = self.buffer.tell()
                    self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
                self.newlines -= 1
                return self.buffer.readline()

            def flush(self):
                if self.writable:
                    os.write(self._fd, self.buffer.getvalue())
                    self.buffer.truncate(0), self.buffer.seek(0)

        class IOWrapper(IOBase):
            def __init__(self, file):
                self.buffer = FastIO(file)
                self.flush = self.buffer.flush
                self.writable = self.buffer.writable
                self.write = lambda s: self.buffer.write(s.encode("ascii"))
                self.read = lambda: self.buffer.read().decode("ascii")
                self.readline = lambda: self.buffer.readline().decode("ascii")

        sys.stdout = IOWrapper(sys.stdout)

    if dfs:
        from types import GeneratorType

        def bootstrap(f, stk=[]):
            def wrappedfunc(*args, **kwargs):
                if stk:
                    return f(*args, **kwargs)
                else:
                    to = f(*args, **kwargs)
                    while True:
                        if type(to) is GeneratorType:
                            stk.append(to)
                            to = next(to)
                        else:
                            stk.pop()
                            if not stk:
                                break
                            to = stk[-1].send(to)
                    return to
            return wrappedfunc

    if hashing:
        RANDOM = random.getrandbits(20)
        class Wrapper(int):
            def __init__(self, x):
                int.__init__(x)

            def __hash__(self):
                return super(Wrapper, self).__hash__() ^ RANDOM

    if read_from_file:
        file = open("input.txt", "r").readline().strip()[1:-1]
        fin = open(file, 'r')
        input = lambda: fin.readline().strip()
        output_file = open("output.txt", "w")
        def fprint(*args, **kwargs):
            print(*args, **kwargs, file=output_file)

    if de:
        def debug(*args, **kwargs):
            # print('\033[92m', end='')
            print(*args, **kwargs)
            # print('\033[0m', end='')
    else:
        def debug(*args, **kwargs):
            pass


    fmax = lambda x, y: x if x > y else y
    fmin = lambda x, y: x if x < y else y

    class lst_lst:
        def __init__(self, n) -> None:
            self.n = n
            self.pre = []
            self.cur = []
            self.notest = [-1] * (n + 1)

        def append(self, i, j):
            self.pre.append(self.notest[i])
            self.notest[i] = len(self.cur)
            self.cur.append(j)

        def iterate(self, i):
            tmp = self.notest[i]
            while tmp != -1:
                yield self.cur[tmp]
                tmp = self.pre[tmp]

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
        tree = [0] * (2 * N) # I think here the 0 is important since it is identity value for sum
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

        tree = [NINF] * (2 * self.N) # I think here the NINF is important since it is identity value for max

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


def solve(segs):
    # debug('------')
    segs.sort(key=lambda tup: tup[1])
    # debug(f'{segs=}')

    maxSegEnd = max([seg[1] for seg in segs])

    # # map point -> how many cats it is in
    # # map point -> rightmost segment end containing this point
    # st = RangeAssignRangeSum([0] * (maxSegEnd + 1)) # st[point] is the rightmost segment end

    # for a, b in segs:
    #     st.rangeAssign(a, b, b)

    # for each index, the current rightmost we can go to
    # process segments in creasing order by left edge
    # maintain our current rightmost as we iterate on the positions

    leftToMax = defaultdict(int)
    for a, b in segs:
        leftToMax[a] = fmax(leftToMax[a], b)

    rightmosts = [0] * (maxSegEnd + 1)
    currRight = 0
    for i in range(len(rightmosts)):
        currRight = fmax(currRight, leftToMax[i])
        rightmosts[i] = currRight

    debug(f'{rightmosts=}')



    # for i in range(1, maxSegEnd + 1):
    #     rightmostAtPointI = st.querySum(i, i) # rightmost at a given point
    #     # print(f'{i=} {rightmostAtPointI=}')

    # stSum = RangeAddRangeMax([0] * (maxSegEnd + 1))
    # for a, b in segs:
    #     stSum.rangeAdd(a, b, 1)

    sums = [0] * (maxSegEnd + 2)
    for a, b in segs:
        sums[a] += 1
        sums[b+1] -= 1
    curr = 0
    for i, v in enumerate(sums):
        curr += v
        sums[i] = curr
    # debug(f'{sums=}')

    # debug(f'{maxSegEnd=}')
    # @lru_cache(maxsize=None)
    cache = [-1] * (maxSegEnd + 2)

    @bootstrap
    def dp(i):
        if cache[i] != -1:
            yield cache[i]
            return
        # debug(f'{i=}')
        if i == maxSegEnd + 1:
            yield 0
            return
        ifSkip = yield dp(i + 1)
        # catsHere = stSum.queryPoint(i)
        catsHere = sums[i]
        # rightmostHere = st.querySum(i, i)
        rightmostHere = rightmosts[i]
        if rightmostHere >= i:
          ifFeed = catsHere + (yield dp(rightmostHere + 1))
        else:
            ifFeed = -inf
        cache[i] = fmax(ifSkip, ifFeed)
        yield fmax(ifSkip, ifFeed)

    print(dp(0))



t = II()
for i in range(t):
    n,m = LII()
    segs = []
    for j in range(m):
        a, b = LII()
        segs.append([a, b])
    solve(segs)