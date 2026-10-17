s = input()

class Node:
    def __init__(self, length):
        self.length = length
        self.suffLink = None # link to the node with the longest proper suffix that is a palindrome
        self.children = {} # maps letter to an eertree node that goes (letter + Node + letter)

negRoot = Node(-1)
emptyRoot = Node(0)
emptyRoot.suffLink = negRoot

prev = negRoot # pointer to the eertree node ending right before us

def findWrappable(node, letter, i):
    length = node.length
    r = i
    l = r - length - 1
    if l < 0 or s[l] != letter:
        return findWrappable(node.suffLink, letter, i)
    return node

res = []
for i, v in enumerate(s):
    # I want to expand the previous node with a letter on both sides
    expandOn = findWrappable(prev, v, i)
    if v in expandOn.children:
        prev = expandOn.children[v]
    else:
        nnode = Node(expandOn.length + 2)
        expandOn.children[v] = nnode
        prev = nnode
        if nnode.length == 1:
            nnode.suffLink = emptyRoot
        else:
            nnode.suffLink = findWrappable(expandOn.suffLink, v, i).children[v]

    res.append(prev.length)

print(*res)