# x, n = map(int, input().split())
# arr = list(map(int, input().split()))

# class Node:
#     def __init__(self, maxPref0, maxSuff0, maxInside, width):
#         self.maxPref0 = maxPref0
#         self.maxSuff0 = maxSuff0
#         self.maxInside = maxInside
#         self.width = width
#         self.left = None
#         self.right = None

# class DynSeg:
#     def __init__(self, low, high):
#         poses = high - low + 1
#         self.low = low
#         self.high = high
#         self.root = Node(poses, poses, poses, poses)
    
#     def pointLight(self, pos):
#        self._pointLight(self.root, self.low, self.high, pos)

#     def _pointLight(self, node, tl, tr, pos):
#         if tl == tr:
#             node.maxPref0 = 0
#             node.maxSuff0 = 0
#             node.maxInside = 0
#             node.width = 1
#             return
#         tm = (tr + tl) // 2
#         if pos <= tm:
#             if not node.left:
#                 node.left = Node(78, 78, 78, 78) # can be dummy values as we will recurse in and pull
#             if not node.right:
#                 rightWidth = (tr - (tm + 1)) + 1
#                 # cannot be dummy values as we aren't recursing into right child
#                 node.right = Node(rightWidth, rightWidth, rightWidth, rightWidth)
#             self._pointLight(node.left, tl, tm, pos)
#         else:
#             if not node.right:
#                 node.right = Node(78, 78, 78, 78) # can be dummy values
#             if not node.left:
#                 leftWidth = (tm - tl) + 1
#                 node.left = Node(leftWidth, leftWidth, leftWidth, leftWidth) # cannot be dummy values
#             self. _pointLight(node.right, tm + 1, tr, pos)
#         self.pull(node)
    
#     def merge(self, left, right):
#         newWidth = left.width + right.width
#         newMaxInside = max(left.maxSuff0 + right.maxPref0, left.maxInside, right.maxInside)
#         newPref = left.maxPref0
#         if left.maxPref0 == left.width:
#             newPref += right.maxPref0
#         newSuff = right.maxSuff0
#         if right.maxSuff0 == right.width:
#             newSuff += left.maxSuff0
#         return Node(newPref, newSuff, newMaxInside, newWidth)

    
#     def pull(self, node):
#         mergedNode = self.merge(node.left, node.right)
#         node.maxPref0 = mergedNode.maxPref0
#         node.maxSuff0 = mergedNode.maxSuff0
#         node.width = mergedNode.width
#         node.maxInside = mergedNode.maxInside
    
#     def queryAll(self):
#         return self.root.maxInside
    
    


# seg = DynSeg(0, x)
# seg.pointLight(0)
# seg.pointLight(x)
# res = []
# for p in arr:
#     seg.pointLight(p)
#     res.append(seg.queryAll() + 1) # max segment width is max consecutive minus 1
# print(*res)

# # 0 1 |2| |3| 4 5 |6| 7 8

x, n = map(int, input().split())
arr = list(map(int, input().split()))

class DynSeg:
    # Each node is identified by an index into these arrays.
    # left[i], right[i] are child indices or -1.
    def __init__(self, low, high):
        self.low = low
        self.high = high

        self.maxPref0 = []
        self.maxSuff0 = []
        self.maxInside = []
        self.width = []
        self.left = []
        self.right = []

        total = high - low + 1
        self.root = self._newNode(total, total, total, total)  # initially all zeros

    def _newNode(self, maxPref0, maxSuff0, maxInside, width):
        i = len(self.width)
        self.maxPref0.append(maxPref0)
        self.maxSuff0.append(maxSuff0)
        self.maxInside.append(maxInside)
        self.width.append(width)
        self.left.append(-1)
        self.right.append(-1)
        return i

    def _makeDefaultNodeForRange(self, tl, tr):
        w = tr - tl + 1
        return self._newNode(w, w, w, w)

    def pointLight(self, pos):
        self._pointLight(self.root, self.low, self.high, pos)

    def _pointLight(self, node, tl, tr, pos):
        if tl == tr:
            self.maxPref0[node] = 0
            self.maxSuff0[node] = 0
            self.maxInside[node] = 0
            self.width[node] = 1
            return

        tm = (tl + tr) // 2

        if pos <= tm:
            if self.left[node] == -1:
                self.left[node] = self._makeDefaultNodeForRange(tl, tm)
            if self.right[node] == -1:
                self.right[node] = self._makeDefaultNodeForRange(tm + 1, tr)
            self._pointLight(self.left[node], tl, tm, pos)
        else:
            if self.right[node] == -1:
                self.right[node] = self._makeDefaultNodeForRange(tm + 1, tr)
            if self.left[node] == -1:
                self.left[node] = self._makeDefaultNodeForRange(tl, tm)
            self._pointLight(self.right[node], tm + 1, tr, pos)

        self._pull(node)

    def _mergeInto(self, leftNode, rightNode):
        newWidth = self.width[leftNode] + self.width[rightNode]

        newMaxInside = max(
            self.maxSuff0[leftNode] + self.maxPref0[rightNode],
            self.maxInside[leftNode],
            self.maxInside[rightNode],
        )

        newPref = self.maxPref0[leftNode]
        if self.maxPref0[leftNode] == self.width[leftNode]:
            newPref += self.maxPref0[rightNode]

        newSuff = self.maxSuff0[rightNode]
        if self.maxSuff0[rightNode] == self.width[rightNode]:
            newSuff += self.maxSuff0[leftNode]

        return newPref, newSuff, newMaxInside, newWidth

    def _pull(self, node):
        L = self.left[node]
        R = self.right[node]
        # in this design, once you start updating, we ensure both children exist
        newPref, newSuff, newInside, newWidth = self._mergeInto(L, R)
        self.maxPref0[node] = newPref
        self.maxSuff0[node] = newSuff
        self.maxInside[node] = newInside
        self.width[node] = newWidth

    def queryAll(self):
        return self.maxInside[self.root]


seg = DynSeg(0, x)
seg.pointLight(0)
seg.pointLight(x)

res = []
for p in arr:
    seg.pointLight(p)
    res.append(seg.queryAll() + 1)  # max gap length = max consecutive zeros + 1
print(*res)
