class Node:
    def __init__(self, val=None, isEnd=False):
        self.val = val
        self.isEnd = isEnd
        self.children = {
            
        } # maps a letter to a trienode

class Trie:
    def __init__(self):
        self.dummy = Node()
    
    def insert(self, word):
        curr = self.dummy
        for i, char in enumerate(word):
            if not char in curr.children:
                newChildNode = Node(char, i == len(word) - 1)
                curr.children[char] = newChildNode
            curr = curr.children[char]
        curr.isEnd = True
    
    def shortestPrefix(self, word):
        curr = self.dummy
        pf = []
        for i, char in enumerate(word):
            if not char in curr.children:
                return None
            curr = curr.children[char]
            pf.append(char)
            if curr.isEnd:
                return ''.join(pf)
        return None
                

class Solution:
    def replaceWords(self, dictionary: List[str], sentence: str) -> str:
        trie = Trie()
        for word in dictionary:
            trie.insert(word)
        resArr = []
        for word in sentence.split():
            triePf = trie.shortestPrefix(word)
            resArr.append(word if triePf == None else triePf)
        return ' '.join(resArr)