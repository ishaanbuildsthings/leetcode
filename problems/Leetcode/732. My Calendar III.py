# class MyCalendarThree:

#     def __init__(self):
#         self.events = [] # holds (time, +1 or -1)

#     def book(self, startTime: int, endTime: int) -> int:
#         self.events.append([startTime, 1])
#         self.events.append([endTime, -1])
#         self.events.sort()
#         curr = 0
#         res = 0
#         for time, diff in self.events:
#             curr += diff
#             res = max(curr, res)
#         return res
        


# # Your MyCalendarThree object will be instantiated and called as such:
# # obj = MyCalendarThree()
# # param_1 = obj.book(startTime,endTime)




























# # TEMPLATE BY https://github.com/agrawalishaan
# # You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

# class Node:
#     def __init__(self, start, end, value=0, lazy=None):
#         self.start = start
#         self.end = end
#         self.value = value
#         self.lazy = lazy
#         self.left = None
#         self.right = None

# class DynamicLazyPropagationSegmentTree:
#     def __init__(self, baseFn, combineFn, applyLazyToValue, combineLazies, lower_bound, upper_bound):
#         self.root = Node(lower_bound, upper_bound)
#         self._combine = combineFn
#         self._baseFn = baseFn
#         self._applyLazyToValue = applyLazyToValue
#         self._combineLazies = combineLazies

#     def _push(self, node):
#         if node.lazy is not None:
#             # print(f"Pushing lazy value at node [{node.start},{node.end}] with lazyValue {node.lazy}")
#             node.value = self._applyLazyToValue(node.lazy, node.value)
#             if node.start != node.end:
#                 if node.left is None:
#                     mid = (node.start + node.end) // 2
#                     node.left = Node(node.start, mid, self._baseFn(0, node.start))
#                     node.right = Node(mid + 1, node.end, self._baseFn(0, mid + 1))
                
#                 if node.left.lazy is None:
#                     node.left.lazy = node.lazy
#                 else:
#                     node.left.lazy = self._combineLazies(node.left.lazy, node.lazy)
                
#                 if node.right.lazy is None:
#                     node.right.lazy = node.lazy
#                 else:
#                     node.right.lazy = self._combineLazies(node.right.lazy, node.lazy)
            
#             node.lazy = None

#     def _updateRange(self, node, l, r, lazyValue):
#         # print(f"Updating range [{l},{r}] with lazyValue {lazyValue} at node [{node.start},{node.end}]")
#         self._push(node)
#         if l > node.end or r < node.start:
#             return  # No overlap
#         if l <= node.start and node.end <= r:
#             node.lazy = lazyValue
#             self._push(node)
#             return
#         mid = (node.start + node.end) // 2
#         if node.left is None:
#             node.left = Node(node.start, mid, self._baseFn(0, node.start))
#             node.right = Node(mid + 1, node.end, self._baseFn(0, mid + 1))
#         self._updateRange(node.left, l, r, lazyValue)
#         self._updateRange(node.right, l, r, lazyValue)
#         node.value = self._combine(node.left.value, node.right.value, node.left.start, node.left.end, node.right.start, node.right.end)

#     def _queryRecurse(self, node, l, r):
#         # print(f"Querying range [{l},{r}] at node [{node.start},{node.end}]")
#         self._push(node)
#         if l > node.end or r < node.start:
#             return None  # No overlap
#         if l <= node.start and node.end <= r:
#             # print(f"Fully in bounds, returning node value: {node.value}")
#             return node.value
#         if node.left is None:
#             return self._baseFn(0, node.start)
#         leftResult = self._queryRecurse(node.left, l, r)
#         rightResult = self._queryRecurse(node.right, l, r)
#         return self._combine(leftResult, rightResult, max(l, node.start), min((node.start + node.end) // 2, r), max((node.start + node.end) // 2 + 1, l), min(r, node.end))

#     def updateRange(self, l, r, lazyValue):
#         self._updateRange(self.root, l, r, lazyValue)

#     def query(self, l, r):
#         return self._queryRecurse(self.root, l, r)

#     def __str__(self):
#         # For visualization or debugging
#         result = []
#         def _printTree(node, indent):
#             if node is None:
#                 return
#             result.append(f'{" " * indent}[{node.start},{node.end}] value: {node.value}, lazy: {node.lazy}')
#             _printTree(node.left, indent + 4)
#             _printTree(node.right, indent + 4)
#         _printTree(self.root, 0)
#         return "\n".join(result)

# class MyCalendarThree:
#     def __init__(self):
#         def baseFn(val, i):
#             return val
        
#         def combineFn(left, right, a, b, c, d):
#             return max(left, right)
        
#         def applyLazy(lazy, val):
#             return lazy + val # like adding 1 to a range
        
#         def combineLazies(oldLazy, newLazy):
#             return oldLazy + newLazy

#         self.st = DynamicLazyPropagationSegmentTree(baseFn, combineFn, applyLazy, combineLazies, 0, 10**9)
    
#     def book(self, startTime: int, endTime: int) -> int:
#         self.st.updateRange(startTime, endTime - 1, 1)
#         return self.st.query(0, 10**9)














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
        
class MyCalendarThree:
    def __init__(self):
        def combineFn(left, right, a, b, c, d):
            return max(left, right)
        
        def applyLazy(lazy, val):
            return lazy + val # like adding 1 to a range
        
        def combineLazies(oldLazy, newLazy):
            return oldLazy + newLazy

        self.st = DynamicLazyPropagationSegmentTree(combineFn, applyLazy, combineLazies, 0, 10**9, 0)
    
    def book(self, startTime: int, endTime: int) -> int:
        self.st.updateRange(startTime, endTime - 1, 1)
        return self.st.query(0, 10**9)