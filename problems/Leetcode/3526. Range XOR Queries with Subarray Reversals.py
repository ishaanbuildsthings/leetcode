class Node:
    def __init__(self, val):
        self.lazyFlipped = False
        self.prio = random.randint(1, 10**9)
        self.sz = 1
        self.xor = val
        self.val = val
        self.l = None
        self.r = None

def pull(node):
    nsize = 1
    nxor = node.val
    for child in [node.l, node.r]:
        if child:
            nsize += child.sz
            nxor ^= child.xor
    node.sz = nsize
    node.xor = nxor

def flip(node):
    if not node:
        return
    node.l, node.r = node.r, node.l

def pushLazy(node):
    if not node:
        return
    if not node.lazyFlipped:
        return
    
    node.lazyFlipped = False

    if node.l:
        node.l.lazyFlipped = not node.l.lazyFlipped
        flip(node.l)
    if node.r:
        node.r.lazyFlipped = not node.r.lazyFlipped
        flip(node.r)

    
def merge(left, right):
    if left == None:
        return right
    if right == None:
        return left
    # left goes above right
    if left.prio < right.prio:
        pushLazy(left)
        left.r = merge(left.r, right)
        pull(left)
        return left
    # right goes above left
    pushLazy(right)
    right.l = merge(left, right.l)
    pull(right)
    return right

def split(node, k):
    if not node:
        return None, None
    onLeft = 0
    if node.l:
        onLeft = node.l.sz
    pos = onLeft + 1
    if pos <= k:
        pushLazy(node)
        portion1, portion2 = split(node.r, k - pos)
        node.r = portion1
        pull(node)
        return node, portion2
    pushLazy(node)
    portion1, portion2 = split(node.l, k)
    node.l = portion2
    pull(node)
    return portion1, node

def pointUpdate(node, i, val):
    pushLazy(node)
    idx = 0
    if node.l:
        idx += node.l.sz
    if i == idx:
        node.val = val
    elif i < idx:
        pointUpdate(node.l, i, val)
    else:
        pointUpdate(node.r, i - idx - 1, val)
    pull(node)

# get [0, left) [left, right] (right, ...] with 0-indexing
def trisect(node, left, right):
    before, rest = split(node, left)
    middle, after = split(rest, right - left + 1)
    return before, middle, after

def join(before, middle, after):
    step1 = merge(before, middle)
    step2 = merge(step1, after)
    return step2

def reverse(node):
    flip(node)
    node.lazyFlipped = not node.lazyFlipped
    
class Solution:
    def getResults(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        res = []
        root = None
        for v in nums:
            node = Node(v)
            root = merge(root, node)
        for qtype, l, r in queries:
            if qtype == 1:
                i = l
                nVal = r
                pointUpdate(root, i, nVal)
            elif qtype == 2:
                left, middle, right = trisect(root, l, r)
                res.append(middle.xor)
                root = join(left, middle, right)
            else:
                left, middle, right = trisect(root, l, r)
                reverse(middle)
                root = join(left, middle, right)
        return res

