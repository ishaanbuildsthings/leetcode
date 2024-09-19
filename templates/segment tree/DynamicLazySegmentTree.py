# TEMPLATE BY https://github.com/agrawalishaan
# You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# Dynamic lazy segment tree!
# combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
# applyLazyToValue: (lazyValue, currentValue) => newValue
# combineLazies: (oldLazy, newLazy) => combinedLazy
# lowerBound: lower bound of the segment tree, often 0
# upperBound: upper bound of the segment tree, often 10**9
# startingValue: the starting value for a node. Usually 0. Like in a normal segment tree, we often pass [0] * n as the starting array. But in a dynamic segment tree there is no array, so we just use a value.

# Example usage: https://leetcode.com/problems/my-calendar-iii/submissions/1375749009/ - fastest TC solution
# falling squares, no coordinate compression needed! https://leetcode.com/problems/falling-squares/submissions/1375749803/
# I tried # of flowers in full bloom but kept getting TLE (python) and MLE (C++), maybe too CPU wise?
# Solved count ingeres in intervals, but slightly modified the template. I did it where when I apply a lazy value to a value, I consider the width of the segment. Like if a segment covers indices [5, 8] and I want to indicate this entire segment is covered, I want the segment to store a 4 (denoting 4 covered numbers) instead of a 1. Ultimately you want to support range assignments but also getting the sum of a range. So each ST node stores the sum in that range, and when I apply a range assignment, it can just update the sum based on the width. Solution: https://leetcode.com/problems/count-integers-in-intervals/submissions/1375789561/
# Also at some point this different formulation worked, but the above one felt natural. In the above one, each node stores the sum, the lazy+value helps update the sum purely based on the width.
#  https://leetcode.com/problems/count-integers-in-intervals/submissions/1375773348/



class Node:
    def __init__(self, start, end, value, lazy=None):
        self.start = start
        self.end = end
        self.value = value
        self.lazy = lazy
        self.left = None
        self.right = None

class DynamicLazyPropagationSegmentTree:
    def __init__(self, combineFn, applyLazyToValue, combineLazies, lowerBound, upperBound, startingValue):
        self.root = Node(lowerBound, upperBound, startingValue)
        self._combine = combineFn
        self._applyLazyToValue = applyLazyToValue
        self._combineLazies = combineLazies
        self._startingValue = startingValue

    def _push(self, node):
        if node is None:
            return
        if node.lazy is not None:
            node.value = self._applyLazyToValue(node.lazy, node.value)
            if node.start != node.end:
                if node.left is None:
                    mid = (node.start + node.end) // 2
                    node.left = Node(node.start, mid, self._startingValue)
                    node.right = Node(mid + 1, node.end, self._startingValue)

                if node.left.lazy is None:
                    node.left.lazy = node.lazy
                else:
                    node.left.lazy = self._combineLazies(node.left.lazy, node.lazy)

                if node.right.lazy is None:
                    node.right.lazy = node.lazy
                else:
                    node.right.lazy = self._combineLazies(node.right.lazy, node.lazy)

            node.lazy = None

    def _updateRange(self, node, l, r, lazyValue):
        if node is None:
            return
        self._push(node)
        if l > node.end or r < node.start:
            return  # No overlap
        if l <= node.start and node.end <= r:
            node.lazy = lazyValue
            self._push(node)
            return
        mid = (node.start + node.end) // 2
        if node.left is None:
            node.left = Node(node.start, mid, self._startingValue)
            node.right = Node(mid + 1, node.end, self._startingValue)
        self._updateRange(node.left, l, r, lazyValue)
        self._updateRange(node.right, l, r, lazyValue)
        node.value = self._combine(
            node.left.value, node.right.value,
            node.left.start, node.left.end,
            node.right.start, node.right.end
        )

    def _queryRecurse(self, node, l, r):
        if node is None:
            return self._startingValue  # Return the starting value for non-initialized nodes
        self._push(node)
        if l > node.end or r < node.start:
            return self._startingValue  # No overlap, return the starting value
        if l <= node.start and node.end <= r:
            return node.value

        mid = (node.start + node.end) // 2

        # Ensure child nodes are initialized before accessing them
        if node.left is None:
            node.left = Node(node.start, mid, self._startingValue)
        if node.right is None:
            node.right = Node(mid + 1, node.end, self._startingValue)

        if l > mid:
            return self._queryRecurse(node.right, l, r)
        elif r <= mid:
            return self._queryRecurse(node.left, l, r)

        leftResult = self._queryRecurse(node.left, l, r)
        rightResult = self._queryRecurse(node.right, l, r)
        return self._combine(
            leftResult, rightResult,
            max(l, node.left.start), min(mid, r),
            max(mid + 1, l), min(r, node.right.end)
        )

    def updateRange(self, l, r, lazyValue):
        self._updateRange(self.root, l, r, lazyValue)

    def query(self, l, r):
        return self._queryRecurse(self.root, l, r)

    def __str__(self):
        # For visualization or debugging
        result = []
        def _printTree(node, indent):
            if node is None:
                return
            result.append(f'{" " * indent}[{node.start},{node.end}] value: {node.value}, lazy: {node.lazy}')
            _printTree(node.left, indent + 4)
            _printTree(node.right, indent + 4)
        _printTree(self.root, 0)
        return "\n".join(result)