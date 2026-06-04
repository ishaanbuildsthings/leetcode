class Node:
    def __init__(self, val=None, cnt=0):
        self.prev = None
        self.nxt = None
        self.val = val
        self.cnt = cnt

class DLL:
    def __init__(self):
        self.L = Node()
        self.R = Node()
        self.L.nxt = self.R
        self.R.prev = self.L

    def append(self, letter, cnt):
        newNode = Node(letter, cnt)
        before = self.R.prev
        after = self.R
        before.nxt = newNode
        after.prev = newNode
        newNode.prev = before
        newNode.nxt = after

    def excise(self, node):
        node.prev.nxt = node.nxt
        node.nxt.prev = node.prev
    
    def empty(self):
        return self.L.nxt == self.R

class Solution:
    def sortString(self, s: str) -> str:
        c = Counter(s)
        dll = DLL()
        for letter, frq in sorted(c.items()):
            dll.append(letter, frq)

        res = []
        
        while not dll.empty():
            curr = dll.L.nxt
            while curr != dll.R:
                res.append(curr.val)
                curr.cnt -= 1
                if curr.cnt == 0:
                    dll.excise(curr)
                curr = curr.nxt
            if dll.empty():
                break
            curr = dll.R.prev
            while curr != dll.L:
                res.append(curr.val)
                curr.cnt -= 1
                if curr.cnt == 0:
                    dll.excise(curr)
                curr = curr.prev
        
        return ''.join(res)
