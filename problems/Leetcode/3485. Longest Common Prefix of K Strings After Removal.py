class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0
        self.maxDepth = 0
        self.parent = None

class Trie:
    def __init__(self, k):
        self.root = TrieNode()
        self.k = k

    def insert(self, word):
        self.root.count += 1
        node = self.root
        for char in word:
            if char not in node.children:
                newChild = TrieNode()
                newChild.parent = node
                node.children[char] = newChild
            node = node.children[char]
            node.count += 1
        self._update(node)

    def remove(self, word):
        self.root.count -= 1
        node = self.root
        for char in word:
            if char not in node.children:
                return
            node = node.children[char]
            node.count -= 1
        self._update(node)

    def _update(self, node):
        while node is not None:
            oldMax = node.maxDepth
            if node.count < self.k:
                node.maxDepth = 0
            else:
                bestChildDepth = 0
                for child in node.children.values():
                    if child.count >= self.k and child.maxDepth > bestChildDepth:
                        bestChildDepth = child.maxDepth
                node.maxDepth = 1 + bestChildDepth
            # if node.maxDepth == oldMax:
            #     break
            node = node.parent

    def getRootMaxDepth(self):
        return self.root.maxDepth


            
class Solution:
    def longestCommonPrefix(self, words: List[str], k: int) -> List[int]:
        t = Trie(k)
        for w in words:
            t.insert(w)
            
        res = [0] * len(words)
        for i in range(len(words)):
            t.remove(words[i])
            res[i] = max(t.getRootMaxDepth() - 1, 0)
            t.insert(words[i])
        return res
        