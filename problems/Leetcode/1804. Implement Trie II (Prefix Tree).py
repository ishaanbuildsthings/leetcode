INSERTS = 400
LENGTH = 2000
class Trie:

    def __init__(self):
        self.nextNode = 1 # root is 0
        self.maxNodes = LENGTH * INSERTS + 1 # include root
        self.passed = [0] * self.maxNodes
        self.ends = [0] * self.maxNodes
        self.children = [{} for _ in range(self.maxNodes)]
        # self.children = defaultdict(dict) # maps cid -> nodeId

    def insert(self, word: str) -> None:
        idx = 0
        self.passed[0] += 1
        for c in word:
            cid = ord(c) - ord('a')
            if cid not in self.children[idx]:
                self.children[idx][cid] = self.nextNode
                self.nextNode += 1
            idx = self.children[idx][cid]
            self.passed[idx] += 1
        self.ends[idx] += 1

    def countWordsEqualTo(self, word: str) -> int:
        idx = 0
        for c in word:
            cid = ord(c) - ord('a')
            if cid not in self.children[idx]:
                return 0
            idx = self.children[idx][cid]
        return self.ends[idx]
        

    def countWordsStartingWith(self, prefix: str) -> int:
        idx = 0
        for c in prefix:
            cid = ord(c) - ord('a')
            if cid not in self.children[idx]:
                return 0
            idx = self.children[idx][cid]
        return self.passed[idx]
        
    def erase(self, word: str) -> None:
        self.passed[0] -= 1
        idx = 0
        for c in word:
            cid = ord(c) - ord('a')
            if cid not in self.children[idx]:
                return
            idx = self.children[idx][cid]
            self.passed[idx] -= 1
        self.ends[idx] -= 1

        


# Your Trie object will be instantiated and called as such:
# obj = Trie()
# obj.insert(word)
# param_2 = obj.countWordsEqualTo(word)
# param_3 = obj.countWordsStartingWith(prefix)
# obj.erase(word)