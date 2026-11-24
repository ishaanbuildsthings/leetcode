class Node:
    def __init__(self, letter):
        self.prev = None
        self.next = None
        self.letter = letter

class DLL:
    def __init__(self):
        self.left = Node(None)
        self.right = Node(None)
        self.left.next = self.right
        self.right.prev = self.left
    
    def evict(self, node):
        before = node.prev
        after = node.next
        before.next = after
        after.prev = before
    
    def append(self, node):
        before = self.right.prev
        before.next = node
        node.prev = before
        node.next = self.right
        self.right.prev = node
    
    def first(self):
        if self.left.next == self.right:
            return None
        return self.left.next
    
    def second(self):
        if not self.first() or self.first().next == self.right:
            return None
        return self.first().next

class Solution:
    def repeatLimitedString(self, s: str, repeatLimit: int) -> str:
        abc = sorted(set(s))
        dll = DLL()
        for letter in abc[::-1]:
            node = Node(letter)
            dll.append(node)

        frq = defaultdict(int)
        for v in s:
            frq[v] += 1

        res = [] # holds (letter, streak)
        while True:
            if not dll.first():
                break

            # can use the max
            canUseMax = False
            nconsec = 0
            if not res:
                canUseMax = True
                nconsec = 1
            else:
                prevLetter, prevConsec = res[-1]
                if dll.first().letter != prevLetter:
                    canUseMax = True
                    nconsec = 1
                elif prevConsec < repeatLimit:
                    canUseMax = True
                    nconsec = prevConsec + 1
                else:
                    canUseMax = False

            if canUseMax:
                mxNode = dll.first()
                mxLetter = mxNode.letter
                frq[mxLetter] -= 1
                if not frq[mxLetter]:
                    dll.evict(mxNode)
                res.append((mxLetter, nconsec))
            else:
                # cannot use the max
                second = dll.second()
                if second is None:
                    break
                res.append((second.letter,1))
                frq[second.letter] -= 1
                if not frq[second.letter]:
                    dll.evict(second)
        
        return ''.join([x for x, _ in res])
