class TrieNode:

    def __init__(self):
        self.top3 = []
        self.children = {} # maps letter -> child trie node

class AutocompleteSystem:

    def __init__(self, sentences: List[str], times: List[int]):
        self.root = TrieNode()
        self.frq = Counter()
        for i in range(len(sentences)):
            self.frq[sentences[i]] = times[i]
            self.upd(sentences[i])
        self.currNode = self.root # also tracked across input calls
        self.currSentence = [] # we track this in a class variable since its stored across calls to input

    def upd(self, sentence):
        node = self.root
        for c in sentence:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
            if sentence not in node.top3:
                node.top3.append(sentence)
            node.top3.sort(key=lambda s: (-self.frq[s], s))
            node.top3 = node.top3[:3]
        

    def input(self, c: str) -> List[str]:
        # handle this case separate
        if c == '#':
            sentence = ''.join(self.currSentence)
            self.frq[sentence] += 1
            self.upd(sentence)
            self.currNode = self.root
            self.currSentence = []
            return []
        self.currSentence.append(c)
        if c not in self.currNode.children:
            self.currNode.children[c] = TrieNode()
        self.currNode = self.currNode.children[c]
        return self.currNode.top3[:]

        
        


# Your AutocompleteSystem object will be instantiated and called as such:
# obj = AutocompleteSystem(sentences, times)
# param_1 = obj.input(c)