class TrieNode:
    def __init__(self):
        self.children = {} # maps a letter to the child trienode
        self.val = 0 # default is 0 since we are using summing
    
class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, val):
        currNode = self.root
        for i, c in enumerate(word):
            if c in currNode.children:
                nextNode = currNode.children[c]
            else:
                nextNode = TrieNode()
                currNode.children[c] = nextNode
            currNode = nextNode
        currNode.val = val
    
    def getSumForPf(self, prefix):
        # navigate to the last letter of prefix
        currNode = self.root
        for i, c in enumerate(prefix):
            if c not in currNode.children:
                return 0
            currNode = currNode.children[c]
        return self.getSumOfSubtree(currNode)
    
    def getSumOfSubtree(self, node):
        return node.val + sum(self.getSumOfSubtree(child) for child in node.children.values())

class MapSum:

    def __init__(self):
        self.trie = Trie()

    def insert(self, key: str, val: int) -> None:
        self.trie.insert(key, val)

    def sum(self, prefix: str) -> int:
        return self.trie.getSumForPf(prefix)


# Your MapSum object will be instantiated and called as such:
# obj = MapSum()
# obj.insert(key,val)
# param_2 = obj.sum(prefix)