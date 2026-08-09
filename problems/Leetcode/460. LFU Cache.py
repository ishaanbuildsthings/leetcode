class Node:
    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val
        self.r = None
        self.l = None

class DLL:
    def __init__(self, capacity):
        self.L = Node()
        self.R = Node()
        self.L.r = self.R
        self.R.l = self.L
    
    def evict(self, node):
        left = node.l
        right = node.r
        left.r = right
        right.l = left
    
    def insertBetween(self, nodeL, nodeR, node):
        nodeL.r = node
        nodeR.l = node
        node.l = nodeL
        node.r = nodeR

class LFUCache:

    def __init__(self, capacity: int):
        self.dll = DLL(capacity)
        self.frqToL = {} # maps a frequency to the leftmost node with that frequency

        # left nodes are the most frequently used, and if tied, the most recently used

        self.keyToNode = {}

        self.nodeToFrq = {}

        self.cap = capacity
    
    def get(self, key: int) -> int:
        return self.getWrap(key)[-1]

    def getWrap(self, key: int):
        node = self.keyToNode.get(key, None)
        if node is None:
            return None, -1

        oldFrq = self.nodeToFrq[node]
        oldLeftHead = self.frqToL[oldFrq]
        nFrq = oldFrq + 1
        oldL = node.l
        oldR = node.r

        self.dll.evict(node)

        # if we were the leftmost, either update our oldFrq left head, or delete it
        if oldLeftHead == node:
            if oldR is not self.dll.R and self.nodeToFrq[oldR] == oldFrq:
                self.frqToL[oldFrq] = oldR
            else:
                del self.frqToL[oldFrq] 

        if nFrq in self.frqToL:
            leftHead = self.frqToL[nFrq]
            self.dll.insertBetween(leftHead.l, leftHead, node)
        elif oldFrq in self.frqToL:
            leftHead = self.frqToL[oldFrq]
            self.dll.insertBetween(leftHead.l, leftHead, node)
        else:
            self.dll.insertBetween(oldL, oldR, node)
        self.frqToL[nFrq] = node

        self.nodeToFrq[node] = nFrq
        
        return node, node.val

    def put(self, key: int, value: int) -> None:
        node, val = self.getWrap(key)

        # if we had a node, we already increased its frequency and moved it, just patch its value now
        if node is not None:
            node.val = value
        else:
            if len(self.keyToNode) == self.cap:
                evicted = self.dll.R.l
                eFrq = self.nodeToFrq[evicted]
                self.dll.evict(evicted)
                if self.frqToL[eFrq] is evicted:
                    del self.frqToL[eFrq]
                del self.keyToNode[evicted.key]
                del self.nodeToFrq[evicted]

            newNode = Node(key, value)
            self.keyToNode[key] = newNode
            self.nodeToFrq[newNode] = 1
            oldHead = self.frqToL.get(1, self.dll.R)
            self.dll.insertBetween(oldHead.l, oldHead, newNode)
            self.frqToL[1] = newNode