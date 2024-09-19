

# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Complexities:
# Build: O(n)
# Space: O(n)
# Query/Update: O(log N)

# baseFn: (val, i) => ...
# combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
# applyLazyToValue: (lazyValue, currentValue) => newValue
# combineLazies: (oldLazy, newLazy) => combinedLazy
# tupleNametags: If baseFn returns a tuple, we can supply nametags for each value, like ('min', 'max'), used for debugging

class LazyPropagationSegmentTree:
    def __init__(self, arr, baseFn, combineFn, applyLazyToValue, combineLazies, tupleNametags=None):
        self.n = len(arr)
        self.arr = arr
        self.tree = [None] * (4 * self.n)
        self.lazy = [None] * (4 * self.n)
        self._combine = combineFn
        self._baseFn = baseFn
        self._applyAggregate = applyLazyToValue
        self._compose = combineLazies
        self.tupleNametags = tupleNametags
        self._build(1, 0, self.n - 1)

    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = self._baseFn(self.arr[tl], tl)
            return
        tm = (tr + tl) // 2
        self._build(2 * i, tl, tm)
        self._build(2 * i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1], tl, tm, tm + 1, tr)

    def _push(self, i, tl, tr):
        if self.lazy[i] is not None:
            # print(f"Pushing lazy value at node {i} [{tl},{tr}] with lazyValue {self.lazy[i]}")
            left_child = 2 * i
            right_child = 2 * i + 1
            self.tree[i] = self._applyAggregate(self.lazy[i], self.tree[i])
            if tl != tr:
                if self.lazy[left_child] is None:
                    self.lazy[left_child] = self.lazy[i]
                else:
                    self.lazy[left_child] = self._compose(self.lazy[left_child], self.lazy[i])

                if self.lazy[right_child] is None:
                    self.lazy[right_child] = self.lazy[i]
                else:
                    self.lazy[right_child] = self._compose(self.lazy[right_child], self.lazy[i])

            self.lazy[i] = None

    def _updateRange(self, i, tl, tr, l, r, lazyValue):
        # print(f"Updating range [{l},{r}] with lazyValue {lazyValue} at node {i} [{tl},{tr}]")
        self._push(i, tl, tr)
        if l > tr or r < tl:
            return  # No overlap
        if l <= tl and tr <= r:
            self.lazy[i] = lazyValue
            self._push(i, tl, tr)
            return
        tm = (tl + tr) // 2
        self._updateRange(2 * i, tl, tm, l, r, lazyValue)
        self._updateRange(2 * i + 1, tm + 1, tr, l, r, lazyValue)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1], tl, tm, tm + 1, tr)

    def _queryRecurse(self, i, tl, tr, l, r):
        # print(f"Querying range [{l},{r}] at node {i} [{tl},{tr}]")
        self._push(i, tl, tr)
        if l > tr or r < tl:
            return None  # No overlap
        if l <= tl and tr <= r:
            # print(f"Fully in bounds, returning node value: {self.tree[i]}")
            return self.tree[i]
        tm = (tl + tr) // 2
        if l > tm:
            # print(f"Left child [{tl},{tm}] would have no overlap, so only using right")
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        elif r < tm + 1:
            # print(f"Right child [{tm+1},{tr}] would have no overlap, so only using left")
            return self._queryRecurse(2 * i, tl, tm, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        combinedResult = self._combine(leftResult, rightResult, max(l, tl), min(tm, r), max(l, tm + 1), min(r, tr))
        # print(f"Combining results for parent [{tl},{tr}] for query [{l},{r}]: left useful: {leftResult}, right useful: {rightResult} -> combined useful: {combinedResult}")
        return combinedResult

    def updateRange(self, l, r, lazyValue):
        self._updateRange(1, 0, self.n - 1, l, r, lazyValue)

    def query(self, l, r):
        return self._queryRecurse(1, 0, self.n - 1, l, r)

    def getVal(self, i):
        return self.arr[i]

    def __str__(self):
        result = []
        def _printTree(i, tl, tr, indent):
            if tl == tr:
                result.append(f'{" " * indent}{self._getPrintFormattedVal(self.tree[i], tl, tr)}')
                return
            tm = (tl + tr) // 2
            result.append(f'{" " * indent}{self._getPrintFormattedVal(self.tree[i], tl, tr)}')
            _printTree(2 * i, tl, tm, indent + 4)
            _printTree(2 * i + 1, tm + 1, tr, indent + 4)
        _printTree(1, 0, self.n - 1, 0)
        return f'{self._line()} SEGMENT TREE VISUALIZATION {self._line()}\n' + "\n".join(result)

    def _getPrintFormattedVal(self, val, tl, tr):
        subarray = self.arr[tl:tr + 1]
        prefix = f'[{tl},{tr}] subarray: {subarray} '
        if self.tupleNametags is None:
            if isinstance(val, tuple):
                return prefix + f"({', '.join(str(v) for v in val)})"
            return prefix + str(val)
        return f'{prefix}({", ".join(f"{tag}: {v}" for tag, v in zip(self.tupleNametags, val))})'

    def _line(self):
        return '________________________________________'


# EXAMPLE LAZY PROP SEGMENT TREE TEMPLATE IN USE:
# https://leetcode.com/problems/falling-squares/submissions/1375688826/
# for falling squares, use a max segment tree (find the max height in a range)
# applyLazy are to set a new max, by using the old max height and the new block. But we can actually just return `lazy` in the applyLazy function since it will always be a higher height in this specific question.
# combineFn of two disjoint ranges, like we want to find the max among those two, is just take the max between them
# combineLazies also uses a max, but we can actually just always use the new lazy, since the new lazy update is always bigger as the heights are always increasing.