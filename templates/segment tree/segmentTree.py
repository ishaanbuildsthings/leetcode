# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Complexities:
# Build: O(n)
# Space: O(n)
# Query/Update: O(log N)

# baseFn: (val, i) => ...
# combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
# tupleNametags: If baseFn returns a tuple, we can supply nametags for each value, like ('min', 'max'), used for debugging

class SegmentTree:
    def __init__(self, arr, baseFn, combine, tupleNametags=None):
        self.n = len(arr)
        self.arr = arr
        self.tree = [None] * (4 * self.n)
        self._combine = combine
        self._baseFn = baseFn
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

    def _queryRecurse(self, i, tl, tr, l, r):
        # print(f"Getting useful intersection from [{tl},{tr}] for query [{l},{r}]")
        if l <= tl and tr <= r:
            # print(f'Fully in bounds, returning node value:')
            # print(f'{self._getPrintFormattedVal(self.tree[i], tl, tr)}\n')
            return self.tree[i]

        tm = (tl + tr) // 2
        # print(f'left child: [{tl},{tm}], right child: [{tm + 1},{tr}]\n')

        if l > tm:
            # print(f'Left child [{tl},{tm}] would have no overlap, so only using right\n')
            return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        elif r < tm + 1:
            # print(f'Right child [{tm+1},{tr}] would have no overlap, so only using left\n')
            return self._queryRecurse(2 * i, tl, tm, l, r)

        leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
        rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
        combinedResult = self._combine(leftResult, rightResult, max(l, tl), min(tm, r), max(l, tm + 1), min(r, tr))
        # print(f"Combining results for parent [{tl},{tr}] for query [{l},{r}]:\n"
        #       f"  left useful: {self._getPrintFormattedVal(leftResult, max(l, tl), min(tm, r))}\n"
        #       f"  right useful: {self._getPrintFormattedVal(rightResult, max(l, tm + 1), min(r, tr))}\n"
        #       f"  -> combined useful: {self._getPrintFormattedVal(combinedResult, max(l, tl), min(r, tr))}\n")
        return combinedResult

    def _updateRecurse(self, i, tl, tr, posToBeUpdated):
        # print(f'descending down to update, pos to be updated: {posToBeUpdated}, current node tl={tl}, tr={tr}')
        if tl == tr:
            # print(f'reached leaf node, updating then going back up and combining')
            self.tree[i] = self._baseFn(self.arr[tl], tl)
            return
        tm = (tl + tr) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2 * i, tl, tm, posToBeUpdated)
        else:
            self._updateRecurse(2 * i + 1, tm + 1, tr, posToBeUpdated)
        self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1], tl, tm, tm + 1, tr)

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

    ################ PUBLIC METHODS START HERE ################

    def updateAndMutateArray(self, index, newVal):
        # print(f'{self._line()} UPDATE CALLED, index={index}, newVal={newVal} {self._line()}')
        self.arr[index] = newVal
        self._updateRecurse(1, 0, self.n - 1, index)
        # print(f'new array: {self.arr}')

    def query(self, l, r):
        # print(f'{self._line()} QUERY CALLED, l={l} r={r} {self._line()}')
        # print(f'array: {self.arr}\n')
        queryResult = self._queryRecurse(1, 0, self.n - 1, l, r)
        # print(f'query result: {queryResult}')
        return queryResult

    # Gets the value at an index in O(1)
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